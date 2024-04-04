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
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
import logging
from sqlalchemy import create_engine, text as satext

import great_expectations as ge
from great_expectations.data_context.types.base import DataContextConfig, DatasourceConfig
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import FilesystemStoreBackendDefaults
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.render.renderer import *
from great_expectations.render.view import DefaultJinjaPageView

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.datasets import TransformDoodle
from enrichsdk.utils import SafeEncoder

logger = logging.getLogger("app")

class CustomGEJSONEncoder(SafeEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except:
            if hasattr(o, "__dict__"):
                return o.__dict__
            else:
                return str(o)

class DataQualityBase(Compute):
    """
    Run data quality checks against a data source based on a spec

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of observability:
            * specified data source
            * custom defined data quality checks (same DSL as Great Expectation python package)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "DataQualityBase"
        self.description = "Data quality checks for a data source given a spec"
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
    # Process the expectations spec
    ###########################################
    def process_spec(self, spec, data):

        if data is None:
            msg = "No dataset loaded" + "\n"
            logger.exception(
                f"Spec: {spec['name']} -- skipping",
                extra={"transform": self.name}
            )
            return None

        # setup a GE object
        df_ge = ge.from_pandas(data)

        name = spec['name']
        config = spec['config']
        expectations = config['expectations']

        # what is the expected result format?
        result_format = config.get('result_format', 'none')
        if result_format not in ["basic", "complete", "boolean_only", "summary"]:
            result_format = "basic"
        result_format = result_format.upper()

        tested_at = datetime.now()

        run_name = f"{name}-{tested_at}"
        run_name = hashlib.md5(run_name.encode('utf-8')).hexdigest()

        # check if checks object is a list
        if not isinstance(expectations, list):
            logger.exception(
                f"Invalid config param -- expectations", extra={"transform": self.name, "data": json.dumps(config, indent=4)}
            )
            return None

        # for each expectation to test
        for expectation in expectations:
            do_test = True

            for f in ['column', 'expectation', 'parameters']:
                if f not in expectation:
                    logger.exception(
                        f"Invalid config param -- expectations", extra={"transform": self.name, "data": json.dumps(config, indent=4)}
                    )
                    do_test = False
                    break
            if do_test is False:
                continue

            # set some params explicitly for the call to GE
            expectation['parameters']['column'] = expectation['column']
            expectation['parameters']['result_format'] = result_format

            # now we can run the expectation test
            if expectation.get('type', 'builtin') == 'builtin':
                method = expectation['expectation']
                params = expectation['parameters']

                if not hasattr(df_ge, method):
                    logger.exception(
                        f"Invalid expectation method", extra={"transform": self.name, "data": json.dumps(expectation, indent=4)}
                    )
                    continue

                # we now have the callback
                callback = getattr(df_ge, method)
                try:
                    r = callback(**params)
                except:
                    logger.exception(
                        f"Error in expectation method", extra={"transform": self.name, "data": json.dumps(expectation, indent=4)}
                    )
                    continue

            elif expectation.get('type', 'builtin') == 'custom':
                pass
            else:
                logger.exception(
                    f"Unknown expectation type", extra={"transform": self.name, "data": json.dumps(expectation, indent=4)}
                )
                continue


        # generate the validataions report
        result_ge = df_ge.validate(run_id=run_name)

        msg = f"Total expectations tested: {len(result_ge['results'])}" + "\n"
        msg += f"{result_ge}"
        logger.debug(
            f"Processed expectations: {spec['name']}",
            extra={"transform": self.name, "data": msg}
        )

        return result_ge


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
            df = pd.read_csv(s3.open(filename), **params)
            return df
        return None

    def get_dataset_s3(self, spec, paths):
        '''
        Gets all files from paths and puts them together
        into a single dataframe. If self.args['cache']==True,
        then this consolidated dataframe is cached / read from cache
        as applicable.
        '''
        msg = ""

        run_date    = self.args['run_date']
        config      = spec['config']
        dataset     = config['dataset']

        cache = self.args.get("cache", False)
        cachename = f"{dataset}-{run_date}"
        cachefile = f"cache/{self.name}-rawdata-cache-" + cachename + ".csv"

        # read from cache if available
        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                msg = f"Location: {cachefile}" + "\n"
                df = pd.read_csv(cachefile)
                logger.debug(f"Read cached {dataset}", extra={"transform": self.name})
                return df

        # read from S3
        dfs = []
        for path in paths:
            _df = self.read_s3_data(path)
            if _df is None:
                msg += f"Path not found, skipping: {path}" + "\n"
                continue
            msg += f"Read from path: {path}" + "\n"
            dfs.append(_df)
        df = pd.concat(dfs)

        logger.debug(f"Read fresh {dataset}", extra={"transform": self.name})

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
                        "objects": [paths],
                    },
                ],
            }

        if not self.state.has_frame(spec['name']):
            self.update_frame(spec, f"Dataset: {dataset}", df, lineage)

        return df


    def get_dataset_db(self, spec):
        name = spec['name']
        config = spec['config']
        source = config['source']

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

    def load_dataset(self, spec):
        name        = spec['name']
        config      = spec['config']

        source_name = config['dataset']
        source_id   = config['source_id']
        source_version = config.get('source_version', 'v1')
        dataset     = config['dataset']

        datacred = self.args['datacred']
        doodle = TransformDoodle(self, self.state, datacred)

        source, paths = doodle.get_source_paths(start=datetime.today() + timedelta(days=-7),
                                                end=datetime.today(),
                                                name=source_name,
                                                version=source_version,
                                                source_id=source_id)

        # Insert a read action..
        try:
            result = doodle.update_source(source['id'], {})
            logger.debug(f"Updated doodle: {source_name}",
                         extra={
                             'transform': self.name,
                             'data': json.dumps(result, indent=4, cls=SafeEncoder)
                         })
        except:
            logger.exception(f"Unable to update doodle {source_name}",
                             extra={
                                 'transform': self.name
                             })

        df = self.get_dataset_s3(spec, paths)

        msg = note(df, f"Input Dataset: {dataset}")
        logger.debug(
            f"Loaded dataset for spec: {name}", extra={"transform": self.name, "data": msg}
        )

        return df

    def s3_store_result(self, spec, result):
        specid      = spec['id']
        appname     = spec.get('app','common')
        name        = spec['name']
        namespace   = spec['namespace']
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()


        # where are we storing it?
        targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")

        resultfile = os.path.join(targetdir, f"health.json")
        metadatafile = os.path.join(targetdir, f"metadata.json")

        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec

        # write to s3
        s = json.dumps(result, indent=4, cls=CustomGEJSONEncoder)
        with s3.open(resultfile, 'w') as fd:
            fd.write(json.loads(s))
        with s3.open(metadatafile, 'w') as fd:
            json.dump(metadata, fd, indent=4, cls=SafeEncoder)

        msg = f"s3 location: {resultfile}" + "\n"
        msg += f"metadata location: {metadatafile}" + "\n"

        logger.debug(f"Wrote data quality results to S3",
                        extra={"transform": self.name,
                                "data": msg})

    def db_store_result(self, spec, result):
        name    = spec['name']
        config  = spec['config']
        store   = config['store']

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

    def store_result(self, spec, result):
        name    = spec['name']
        config  = spec['config']
        store   = config.get('store', {"sink": "s3"})

        for f in ["sink"]:
            if f not in store:
                logger.exception(
                    f"Store has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                return

        sink = store['sink']
        if sink == "s3":
            # store in s3
            self.s3_store_result(spec, result)
        elif sink == "db":
            # store in db
            self.db_store_result(spec, result)
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

    ###########################################
    # Expectation Testing Functions
    ###########################################

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.dataqualityv2")
        if is_valid:
            logger.debug(
                f"Loaded profilespec",
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
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                do_process_spec = False
                continue

            for f in ["name", "config"]:
                if f not in spec:
                    logger.exception(
                        f"Spec has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue

            config = spec['config']

            for f in ["source_id", "expectations"]:
                if f not in config:
                    logger.exception(
                        f"Spec config has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue

            ## we can now proceed with processing the spec
            # frist, load the source data
            data = self.load_dataset(spec)

            # then, process it
            result = self.process_spec(spec, data)
            if result is None:
                continue

            ## store the expectation validation result
            self.store_result(spec, result)


        # Done
        logger.debug(
            "Complete execution", extra=self.config.get_extra({"transform": self.name})
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
