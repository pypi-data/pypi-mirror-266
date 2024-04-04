import os
import json
from json import JSONEncoder
import pickle
import numpy as np
import pandas as pd
import time
import sqlite3
import tempfile
import hashlib
import builtins

from datetime import datetime, timedelta, date
import logging
from sqlalchemy import create_engine, text as satext

from dateutil import parser as dateparser

from enrichsdk import Compute, S3Mixin
from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.datasets import TransformDoodle
from enrichsdk.utils import SafeEncoder

logger = logging.getLogger("app")

class DataSanitizerBase(Compute):
    """
    Sanitize data based on rules.

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of transformations
            * specified data source
            * custom defined rules
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "DataSanitizerBase"
        self.description = "Sanitize data based on rules"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

    @classmethod
    def instantiable(cls):
        return False

    def get_handlers(self, spec):
        """
        Define various callbacks that take a dataframe, spec
        and compute.
        """
        return {}

    ###########################################
    # Process the transformation spec
    ###########################################
    def process_spec(self, spec, df):

        if df is None:
            logger.exception(
                f"Spec: {spec['name']} -- No data",
                extra={"transform": self.name}
            )
            return None

        transformations = spec['transformations']

        # Now apply the transformations
        msg = ""
        for i, t in enumerate(transformations):
            name = f"xform{i}"
            if not isinstance(t, dict):
                msg += f"[{name}] Skipped. Not a dict\n"
                continue
            name = t.get('name', name)
            method = t.get('method')
            if method is None:
                msg += f"[{name}] No method specified \n"
                continue
            params = t.get('params', {})
            if callable(method):
                func = method
            elif hasattr(self, method):
                func = getattr(self, method)
            elif method in builtins:
                func = getattr(builtin, method)
            else:
                msg += f"[{name}] Invalid method\n"
                continue

            nature = t.get('nature', 'column')
            if nature == "column": 
                columns = t.get('columns', [])
                if len(columns) == 0:
                    msg += f"[{name}] No columns specified\n"
                    continue
                for c in columns:
                    if c not in df.columns:
                        msg += f"[{name}] {c} - Invalid column\n"
                        continue
                    try:
                        df[c] = func(df[c], params)
                        msg += f"[{name}] {c} Done\n"
                    except Exception as e:
                        msg += f"[{name}] {c} - Error! str(e)\n"
                        continue
            else:
                msg += f"[{name}] Unsupported nature: {nature}\n"
                continue
            
        logger.debug(
            f"Processed transformation: {spec['name']}",
            extra={"transform": self.name, "data": msg}
        )

        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "dataframe",
                    "nature": "input",
                    "objects": [spec['name']] 
                    },
                ],
            }        
        self.update_frame(spec['name']+"-transformed", f"Transformed Dataset: {spec['name']}", df, lineage)
        
        return df, msg


    ###########################################
    # Helper Functions
    ###########################################

    def update_frame(self, source, description, df, lineage=None):
        if isinstance(source, str):
            name = source
        else:
            name = source["name"]

        params = self.get_column_params(name, df)
        if lineage is not None:
            if isinstance(lineage, dict):
                params.append(lineage)
            else:
                params.extend(lineage)

        detail = {
            "name": name,
            "df": df,
            "frametype": "pandas",
            "description": description,
            "params": params,
            "transform": self.name,
            "history": [],
        }

        self.state.update_frame(name, detail)

    ###########################################
    # I/O Functions
    ###########################################

    def read_s3_data(self, filename, params={}):
        # assume we have a resolved s3fs object
        s3 = self.args['s3']
        if s3.exists(filename):
            try:
                df = pd.read_csv(s3.open(filename), **params)
                return df
            except:
                pass
        return None

    def get_dataset_s3(self, spec, source, paths, start_date, end_date):
        '''
        Gets all files from paths and puts them together
        into a single dataframe. If self.args['cache']==True,
        then this consolidated dataframe is cached / read from cache
        as applicable.
        '''
        msg = ""

        run_date    = self.args['run_date']
        dataset     = source['dataset']
        params      = source.get('params', {})

        cache = self.args.get("cache", False)
        cachename = f"{dataset}-{start_date}-to-{end_date}"
        cachefile = f"cache/{self.name}-rawdata-cache-" + cachename + ".csv"

        # read from cache if available
        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                msg = f"Location: {cachefile}" + "\n"
                df = pd.read_csv(cachefile, **params)
                logger.debug(f"Read cached {dataset}", extra={"transform": self.name, "data": msg})
                return df

        # read from S3
        dfs = []
        for path in paths:
            _df = self.read_s3_data(path, params)
            if _df is None:
                msg += f"Path error, skipping: {path}" + "\n"
                continue
            msg += f"Read from path: {path}" + "\n"
            dfs.append(_df)
        df = pd.concat(dfs)

        logger.debug(f"Read {dataset}", extra={"transform": self.name})

        # Cache it for future use
        if cache:
            df.to_csv(cachefile, index=False)

        # Insert lineage if possible
        lineage = None
        if (len(paths) > 0):
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": paths,
                    },
                ],
            }

        if not self.state.has_frame(spec['name']):
            self.update_frame(spec['name'] + "-raw", f"Raw Dataset: {spec['name']}", df, lineage)

        return df    

    def get_dataset_db(self, spec):
        name = spec['name']
        source = spec['source']

        testmode = self.args.get('testmode', False)
        env      = 'test' if testmode else 'prod'

        # Get the db engine
        engine_name = source['params'][env]['engine']
        engine = self.engines[engine_name]

        # Get the query
        query = source['params'][env]['query']
        if query.endswith('.sql'):
            # we have a file containing the query
            sqlfile = os.path.join(self.scriptdir, query)
            query = open(sqlfile).read()

        df = self.read_db_source(engine, query)

        # Now the input load...
        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "database",
                    "nature": "input",
                    "objects": [source['dataset']],
                },
            ],
        }

        self.update_frame(spec, f"Dataset: {name}", df, lineage)

        return df

    def read_db_source(self, engine, query):
        # Run the query
        df = pd.read_sql_query(satext(query), con=engine)

        return df

    def get_datewindow(self, source, spec):
        datewindow = {}
        default_delta = 180

        msg = ""
        start_date_str = source.get('start_date')
        end_date_str = source.get('end_date')

        if not end_date_str:
            msg += f"End date not specified. Using default as yesterday's date\n"
            end  = self.args['run_date'] # yesterday
            end_date_str = end.isoformat()

        if not start_date_str:
            msg += f"start date not specified. Using default as 180 days prior to end date\n"
            start = dateparser.parse(end_date_str).date() + timedelta(days=-default_delta)
            start_date_str = start.isoformat()

       # If start and end dates are specified, check if date is parseable
        try:
            start_date = dateparser.parse(start_date_str).date()
            end_date = dateparser.parse(end_date_str).date()
        except:
            logger.exception(
                        f"Invalid start date or end date. Skipping {spec['name']}.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4, cls=SafeEncoder)}
                    )
            datewindow = None # be explicit
            return datewindow

        if start_date > end_date:
            logger.exception(
                        f"Start date > end date. Skipping {spec['name']}.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4, cls=SafeEncoder)}
                    )
            datewindow = None # be explicit
            return datewindow

        datewindow['start_date'] = start_date
        datewindow['end_date'] = end_date

        logger.debug(
            f"{spec['name']}: {datewindow['start_date']} to {datewindow['end_date']}",
            extra={"transform": self.name, "data": json.dumps(datewindow, indent=4, cls=SafeEncoder)}
        )        
        return datewindow
    
    def load_dataset(self, spec, source, datewindow):
        msg = ""

        source_id       = source.get('id', source.get('source_id', None))
        dataset         = source['dataset']
        source_version  = source.get('source_version', 'v1')
        nature          = source.get('nature', 's3')

        start_date      = datewindow['start_date']
        end_date        = datewindow['end_date']

        if source_id == "custom":
            # we have a custom defined method in the derived class to generate the dataset
            if not hasattr(self, dataset):
                logger.exception(
                    f"No handler for: {dataset}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4, cls=SafeEncoder)}
                )
                return None

            handler = getattr(self, dataset)
            params = source.get("params", {})
            df = handler(start_date, end_date, params)
            if df is None:
                logger.exception(
                    f"Couldn't load dataset for {spec['name']}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4, cls=SafeEncoder)}
                )
                return None

            msg += f"Loaded using custom method: {dataset}" + "\n"
        else:

            if source_id is None and dataset is None:
                logger.error(
                    f"source id and name missing",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4, cls=SafeEncoder)}
                )                
                return None

            # we are using the SDK to get the dataset
            datacred = self.args['datacred']
            doodle = TransformDoodle(self, self.state, datacred)

            # Now get the source details...
            d_source, paths = doodle.get_source_paths(start=start_date,
                                                      end=end_date,
                                                      name=dataset,
                                                      version=source_version,
                                                      source_id=source_id)

            msg += f"Paths: {paths}" + "\n"

            # Insert a read action..
            try:
                result = doodle.update_source(d_source['id'], {})
                logger.debug(f"Updated Doodle: {dataset}",
                             extra={
                                 'transform': self.name,
                                 'data': json.dumps(result, indent=4, cls=SafeEncoder)
                             })
            except:
                logger.exception(f"Unable to update Doodle {dataset}",
                                 extra={
                                     'transform': self.name
                                 })

            if nature == "s3":
                # read the data from S3
                df = self.get_dataset_s3(spec, source, paths, start_date, end_date)
            else:
                logger.error(f"Unable to access raw data",
                             extra={
                                 'transform': self.name
                             })                


        # check if we need to perform a post-processing step on the input data
        postprocess = source.get("postprocess")
        if postprocess != None:
            if not hasattr(self, postprocess['method']):
                logger.exception(
                    f"No post-process handler for: {dataset}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4, cls=SafeEncoder)}
                )
            else:
                handler = getattr(self, postprocess['method'])
                params = postprocess.get("params", {})
                df = handler(df, params)
                msg += f"Post-processed dataset={dataset} using handler: {postprocess}" + "\n"

        msg += note(df, f"Input Dataset: {dataset}")
        logger.debug(
            f"Loaded dataset {dataset}",
            extra={"transform": self.name, "data": msg}
        )

        return df    

    def s3_store_result(self, spec, result, extra):
        name        = spec['name']
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()


        # where are we storing it?
        targetdir = os.path.join(self.args['s3root'], f"{name}/{run_date}/{epoch}")

        resultfile = os.path.join(targetdir, f"data.csv")
        metadatafile = os.path.join(targetdir, f"metadata.json")

        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec
        metadata.update(extra)
        
        # write to s3
        s = json.dumps(result, indent=4, cls=SafeEncoder)
        with s3.open(resultfile, 'w') as fd:
            result.to_csv(fd, index=False)
        with s3.open(metadatafile, 'w') as fd:
            json.dump(metadata, fd, indent=4, cls=SafeEncoder)

        msg = f"s3 location: {resultfile}" + "\n"
        msg += f"metadata location: {metadatafile}" + "\n"

        logger.debug(f"Wrote final results to S3: {name}",
                        extra={"transform": self.name,
                                "data": msg})

    def db_store_result(self, spec, result, extra):
        name    = spec['name']
        store   = spec['store']

        testmode = self.args.get('testmode', False)
        env      = 'test' if testmode else 'prod'

        # Get the db engine
        engine_name = store['params'][env]['engine']
        engine = self.engines[engine_name]

        # write results to db
        table_name = store['params'][env]['table']
        ret = results.to_sql(table_name,
                            engine,
                            if_exists='append',
                            index=False)
        # write data to db
        data_table_name = name.replace('-','_')
        ret = data.to_sql(data_table_name,
                            engine,
                            if_exists='append',
                            index=False)

        msg = f"DB engine: {engine}" + "\n"

        logger.debug(f"Wrote monitor results to DB",
                        extra={"transform": self.name,
                                "data": msg})

    def store_result(self, spec, result, extra):
        name    = spec['name']
        store   = spec.get('store', {"sink": "s3"})

        for f in ["sink"]:
            if f not in store:
                logger.exception(
                    f"Store has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4, cls=SafeEncoder)}
                )
                return

        sink = store['sink']
        if sink == "s3":
            # store in s3
            self.s3_store_result(spec, result, extra)
        elif sink == "db":
            # store in db
            self.db_store_result(spec, result, extra)
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

    ###########################################
    # Implement the data transformation logic...
    ###########################################
    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra={"transform": self.name}
        )

        # Will be used in other places..
        self.state = state

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.dataqualityv2")
        if is_valid:
            name = profile.get('name', 'unknown')
            logger.debug(
                f"Loaded profilespec: {name}",
                extra={"transform": self.name, "data": msg}
            )
        else:
            logger.error(
                f"Could not load profilespec",
                extra={"transform": self.name, "data": msg}
            )
            raise Exception("could not load profilespec")

        specs = profile.get("specs", None)
        if specs is None:
            raise Exception("Could not find 'specs' in profile")

        # Now go through each spec and process it
        for spec in specs:

            ## first, some checks on the spec
            do_process_spec = True
            name = spec.get('name', 'NO_SPEC_NAME')

            enabled = spec.get("active", True)
            if not enabled:
                logger.debug(
                    f"Spec not enabled, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4, cls=SafeEncoder)}
                )
                do_process_spec = False
                continue

            for f in ["name", "source", "transformations"]:
                if f not in spec:
                    logger.exception(
                        f"Spec has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4, cls=SafeEncoder)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue

            ## we can now proceed with processing the spec            
            source = spec['source']
            
            # get time_window for indicator and observation data set
            datewindow = self.get_datewindow(source, spec)
            if datewindow is None :
                do_process_spec = False
                continue
            
            ## we can now proceed with processing the spec
            # first, load the source data
            data = self.load_dataset(spec, source, datewindow)

            # then, process it
            result, msg = self.process_spec(spec, data)
            if result is None:
                continue

            ## store the expectation validation result
            self.store_result(spec, result, {'notes': msg})


        # Done
        logger.debug(
            "Complete execution", extra={"transform": self.name}
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
