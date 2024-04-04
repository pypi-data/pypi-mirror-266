import io
import os
import json
import math
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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.contrib.lib.assets import BaseProphetForecasterModel
from enrichsdk.datasets import TransformDoodle
from enrichsdk.utils import SafeEncoder, get_yesterday


from dateutil import parser as dateparser

logger = logging.getLogger("app")

class TimeSeriesForecasterBase(Compute):
    """
    Take a timeseries and project it's future values with exogenous variables.
    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of time series forecasting
            * specified data source or custom method to generate one
            * by default, forecast using facebook's prophet library
             or custom defined ones using other libraries
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "TimeSeriesForecasterBase"
        self.description = "Forecast future values of a timeseries"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

        self.default_strategy = "prophet"
        self.default_type = "vanilla"

        self.epoch = time.time()    #for output path


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
    # Process the forecaster spec
    ###########################################
    def process_spec(self, spec, data):
        """
        Process the forecaster spec.
        generate result and chart for each forecaster
        """

        def store_chart(tsf):
            '''
            We generate multiple charts for each forecaster
            Immeidately store the charts as we generate
            '''
            viz = tsf['viz']
            filename = f"{forecaster_name}-{name}-forecasting.png"
            msg = self.store_viz(spec, filename, viz)
            tsf.pop('viz', None)
            return msg

        msg = ""
        name = spec["name"]
        config = spec["config"]

        forecasters = config['forecasters']

       # if forecasters is not a dict
        if not isinstance(forecasters, dict):
            logger.exception("Forecasters must be a dict",
                             extra={"transform": self.name})
            raise Exception("Forecasters must be a dict")

        forecasters = config['forecasters']

        result = {"forecasts": {}}
        for forecaster_name, forecaster in forecasters.items():

            tsf = self.run_forecasting(spec, data, forecaster_name, forecaster)
            msg+= store_chart(tsf)

            logger.debug(f"Processed and then aved visualization for {forecaster_name}",
                    extra={"transform": self.name, "data": msg})

            result['forecasts'][forecaster_name] = tsf

        logger.debug(f"Done processing all the forecasters",
                extra={"transform": self.name})

        return result


    def run_forecasting(self, spec, data, forecaster_name, forecaster):
        """
        Instantiate the forecaster and run forecasting
        """
        # default is prophet
        # type is vanilla
        strategy = forecaster.get('strategy', self.default_strategy)
        type = forecaster.get('type', self.default_type)
        params = forecaster.get('params', {})

        # return timeseries forecast
        tsf = {}
        chart_params = params.get('chart_params', {})

        if strategy == 'prophet':

            if type == "vanilla":
                observation  = params.get('observation', None)

                if observation is None:
                    logger.exception(f"Observation time series must be specified for forecaster: {forecaster_name}",
                                    extra={"transform": self.name, "data": json.dumps(forecaster, indent=4)})
                    raise Exception("Observation must be specified for prophet forecaster")

                df = data['observations'][observation]

                forecast_obj = BaseProphetForecasterModel(df)
                forecast = forecast_obj.run_forecasting(params)

                viz = forecast_obj.visualize_forecasting(forecast, chart_params)
                del forecast_obj

            elif type ==  "exogenous":
                df = data['combined']

                forecast_obj = BaseProphetForecasterModel(df)
                forecast = forecast_obj.run_forecasting(params)
                viz = forecast_obj.visualize_forecasting(forecast, chart_params)
                del forecast_obj

            else:
                logger.excption(f"Invalid type for prophet forecaster: {forecaster_name}",
                                extra={"transform": self.name, "data": json.dumps(forecaster, indent=4)})
                raise Exception("Invalid type for prophet forecaster")

        tsf = {
            "forecast" : forecast,
            "viz" : viz,
        }
        msg = note(forecast, f"Forecast for {forecaster_name}")
        logger.debug(f"Forecasted time series for {forecaster_name}",
                        extra={"transform": self.name, "data": msg})

        return tsf


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
        config      = spec['config']
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
                        "objects": paths,
                    },
                ],
            }

        if not self.state.has_frame(spec['name']):
            self.update_frame(spec, f"Dataset: {dataset}", df, lineage)

        return df

    def load_dataset(self, spec, name, source, datewindow):
        msg = ""

        source_id       = source['source_id']
        dataset         = source['dataset']
        source_version  = source.get('source_version', 'v1')

        start_date      = datewindow['start_date']
        end_date        = datewindow['end_date']

        if source_id == "custom":
            # we have a custom defined method in the derived class to generate the dataset
            if not hasattr(self, dataset):
                logger.exception(
                    f"No handler for: {dataset}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4)}
                )
                return None

            handler = getattr(self, dataset)
            params = source.get("params", {})
            df = handler(start_date, end_date, params)
            if df is None:
                logger.exception(
                    f"Couldn't load dataset for {spec['name']}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4)}
                )
                return None

            msg += f"Loaded using custom method: {dataset}" + "\n"
        else:
            # we are using the SDK to get the dataset
            datacred = self.args['datacred']
            doodle = TransformDoodle(self, self.state, datacred)

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

            # read the data from S3
            df = self.get_dataset_s3(spec, source, paths, start_date, end_date)


        # check if we need to perform a post-processing step on the input data
        postprocess = source.get("postprocess")
        if postprocess != None:
            if not hasattr(self, postprocess['method']):
                logger.exception(
                    f"No post-process handler for: {dataset}",
                    extra={"transform": self.name, "data": json.dumps(source, indent=4)}
                )
            else:
                handler = getattr(self, postprocess['method'])
                params = postprocess.get("params", {})
                df = handler(df, params)
                msg += f"Post-processed dataset={dataset} using handler: {postprocess}" + "\n"

        msg += note(df, f"Input Dataset: {dataset}")
        logger.debug(
            f"Loaded dataset={dataset} for source={name}",
            extra={"transform": self.name, "data": msg}
        )

        return df

    def store_viz(self, spec, filename, viz):
        appname     = spec.get('app', self.name)
        name        = spec['name']
        namespace   = spec.get('namespace', 'default')
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = self.epoch

        msg = ""

        # write to s3
        targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")
        vizfile = os.path.join(targetdir, f"{filename}")

        img_data = io.BytesIO()
        viz.savefig(img_data, format='png')
        img_data.seek(0)
        with s3.open(vizfile, 'wb') as fd:
            fd.write(img_data.getbuffer())

        msg += f"Stored (remote): {vizfile}" + "\n"

        return msg


    def s3_store_result(self, spec, result):
        appname     = spec.get('app',self.name)
        name        = spec['name']
        namespace   = spec.get('namespace', 'default')
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = self.epoch


        # where are we storing it?
        targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")

        metadatafile = os.path.join(targetdir, f"metadata.json")
        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec

        ## write to s3
        # forecast dfs
        msg = ""
        for forecaster_name in result[name].get("forecasts", {}):
            resultfile = os.path.join(targetdir, f"forecast_{forecaster_name}.csv")
            msg += f"Forecast for {forecaster_name}: {resultfile}" + "\n"
            with s3.open(resultfile, 'w') as fd:
                result[name]["forecasts"][forecaster_name]['forecast'].to_csv(fd, index=False)

        # extras
        if "extra" in result[name]:
            resultfile = os.path.join(targetdir, f"extra.json")
            msg += f"Extras for {forecaster_name}: {resultfile}" + "\n"
            with s3.open(resultfile, 'w') as fd:
                json.dump(result[name]['extra'], fd, indent=4, cls=SafeEncoder)

        # metadata
        msg += f"Metadata location: {metadatafile}" + "\n"
        with s3.open(metadatafile, 'w') as fd:
            json.dump(metadata, fd, indent=4, cls=SafeEncoder)

        logger.debug(f"Wrote timeseries forecasting result to S3",
                        extra={"transform": self.name,
                                "data": msg})


    def store_result(self, spec, result):
        name    = spec['name']
        config  = spec['config']
        store   = config.get('store', {"sink": "s3"})
        stored  = False

        for f in ["sink"]:
            if f not in store:
                logger.exception(
                    f"Store has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                return

        sink = store['sink']
        if sink == "s3":
            try:
                # store in s3
                self.s3_store_result(spec, result)
                stored = True
            except:
                pass
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

        # update KPI for this spec
        self.state.update_kpi(f"{name}_ts_forecasted", stored)


    def get_datewindow(self, source, spec):
        """
        Set the time window for observations and exogenous variables.
        Get both of these from args parameters
        if not start_date defaults to 60 days prior to end date
        end_date is day prior to run_date, which is usually today
        """
        datewindow = {}
        default_delta = 60

        run_date = self.args['run_date']

        try:
            if 'end_date' in self.args and self.args['end_date']:
                end_date = datetime.fromisoformat(self.args['end_date'])
            else:
                logger.debug(
                    f"End date not in args. Using yesterday's date.")
                end_date = run_date - timedelta(days=1)

            if 'start_date' in self.args and self.args['start_date']:
                start_date = datetime.fromisoformat(self.args['start_date'])
            else:
                logger.debug(
                    f"Start date not in args. Using {default_delta} days prior to end date. ")
                start_date = end_date - timedelta(days=default_delta)
        except Exception as e:
            logger.exception(
                f"Error parsing date window for {spec['name']}.",
                extra={"transform": self.name, "data": self.args}
            )
            datewindow = None
            return datewindow

        if start_date > end_date:
            logger.exception(
                        f"Start date greater than end date. Skipping the spec {spec['name']}.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
            datewindow = None # be explicit
            return datewindow

        datewindow['start_date'] = start_date
        datewindow['end_date'] = end_date

        return datewindow

    ######################################################################
    ## Helper functions for process
    ######################################################################
    def precheck_spec(self, spec):
        '''
        Check if the spec is valid
        '''
        is_valid_spec = True
        name = spec.get('name', 'NO_SPEC_NAME')

        enabled = spec.get("active", True)
        if not enabled:
            logger.debug(
                f"Spec not enabled, skipping.",
                extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
            )
            is_valid_spec = False
            return is_valid_spec

        for f in ["name", "config"]:
            if f not in spec:
                logger.exception(
                    f"Spec has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                is_valid_spec = False
                return is_valid_spec

        config = spec['config']

        for f in ["source", "forecasters"]:
            if f not in config:
                logger.exception(
                    f"Spec config has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                is_valid_spec = False
                return is_valid_spec

        return is_valid_spec

    def load_source(self, spec):
        """
        Load all the sources to a 'data' dict
        modifies the 'data' dict.
        """
        config = spec['config']
        source = config['source']

        data = {}
        is_valid = True

        if 'observations' not in source:
            logger.exception(
                f"Spec config has no observations param, skipping.",
                extra={"transform": self.name, "data": json.dumps(spec, indent=4)})
            is_valid_spec = False
            return is_valid

        if 'exovars' not in source:
            logger.debug(
                f"Exogenous variables not specified in {spec['name']}",
                extra={"transform": self.name, "data": json.dumps(spec, indent=4)})

        # get time_window for observations and exovars
        datewindow = self.get_datewindow(source, spec)
        if datewindow is None:
            logger.debug(
                f"Invalid date window for {spec['name']}",
                extra={"transform": self.name})
            is_valid_spec = False
            return is_valid, data

        data['observations'] = {}
        for dataname, dataspec in source['observations'].items():
            dataset = self.load_dataset(spec, dataname, dataspec, datewindow)
            data["observations"][dataname] = dataset

        # then load the exovars data set if specified
        if "exovars" in source:
            data['exovars'] = {}
            for dataname, dataspec in source['exovars'].items():
                dataset = self.load_dataset(spec, dataname, dataspec, datewindow)
                data["exovars"][dataname] = dataset

        return is_valid, data

    def combined_dataset(self, spec, data):
        """
        Adds the combined dataset to the data dict
        """
        config = spec['config']
        combined_dataset = pd.DataFrame()

        if "combine_sources" in config:
            combine_sources = config["combine_sources"]
            dataset = combine_sources.get("dataset", None)

            if hasattr(self, dataset):
                params = combine_sources.get("params", {})
                handler = getattr(self, dataset)
                combined_dataset =  handler(params, data, spec)
                data['combined'] = combined_dataset

                msg = note(combined_dataset, "Combined dataset")
                logger.debug(f"Combined dataset for {spec['name']}",
                             extra={"transform": self.name, "data": msg})

        return data

    def postprocess_results(self, spec, result):
        """
        Postprocess the results. The method defined in the subclass
        """
        config = spec['config']
        # do post_process results
        postprocess_results = config.get('postprocess_results', None)
        if postprocess_results:
            method = postprocess_results.get('method', "")
            params = postprocess_results.get('params', {})
            handler = getattr(self, method, None)
            if handler:
                result = handler(spec, result, params)
            else:
                logger.exception(
                    f"Spec: {spec['name']} -- postprocess_results method not found",
                    extra={"transform": self.name}
                )
        logger.debug(f"Postprocess results for {spec['name']} done",
                     extra={"transform": self.name})

        return result


    ###########################################
    # Main function
    ###########################################
    def process(self, state):
        """
        Run the computation and update the state
        1. Load the datasets
        2. Run forecasting
        3. process the forecasting results
        4. store the results
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.forecasting")
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

            do_process_spec = self.precheck_spec(spec)
            if do_process_spec == False:
                continue

            ## we can now proceed with processing the spec
            # load source
            do_process_spec, data = self.load_source(spec)
            if do_process_spec == False:
                continue

            # post process the sources
            data = self.combined_dataset(spec, data)

            # run the forecasters
            result = self.process_spec(spec, data)
            if result is None:
                continue

            # postprocess the results
            result = self.postprocess_results(spec, result)

            # tag the result under the spec name
            result = {spec['name']: result}

            # store the  results
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
