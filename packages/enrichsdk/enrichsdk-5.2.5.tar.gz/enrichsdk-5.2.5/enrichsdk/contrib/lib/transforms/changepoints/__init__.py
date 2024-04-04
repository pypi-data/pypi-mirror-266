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
from enrichsdk.contrib.lib.assets import BaseChangePointDetectorModel
from enrichsdk.datasets import TransformDoodle
from enrichsdk.utils import SafeEncoder

from dateutil import parser as dateparser

logger = logging.getLogger("app")

class ChangePointDetectorBase(Compute):
    """
    Take a timeseries signal and identify changepoints in the signal

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of change point detection:
            * specified data source or custom method to generate one
            * generic change point detection method or custom defined ones
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "ChangePointDetectorBase"
        self.description = "Change point(s) detection for a timeseries signal given a spec"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

        self.cautions = {
            "low": {"color": "green", "desc": "MINIMAL", "rec": "In a BUSINESS-AS-USUAL regime now."},
            "medium": {"color": "gold", "desc": "LOW to MODERATE", "rec": "Expect LOW to MODERATE swings in this regime."},
            "high": {"color": "red", "desc": "HIGH to EXTREME", "rec": "Stay alert for HIGH to EXTREME swings in this regime."},
        }

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
    # Process the change points detection spec
    ###########################################
    def process_spec(self, spec, data):
        msg = ""

        if data is None:
            msg = "No dataset loaded" + "\n"
            logger.exception(
                f"Spec: {spec['name']} -- skipping",
                extra={"transform": self.name}
            )
            return None

        name = spec["name"]
        config = spec["config"]

        # use the specified strategy to detect change points
        detector = config['detector']
        method = detector.get('method', 'default')
        if method == "default":
            # we use the default strategy
            r = self.process_spec_default(spec, data)
        else:
            # Custom callback
            r = self.process_spec_custom(spec, data)

        # The spec processor can return multiple dataframes
        result = {name: r}

        logger.debug(
            f"Processed changepoint detection",
            extra={"transform": self.name, "data": json.dumps(result, indent=4, cls=SafeEncoder)}
        )

        return result

    def process_spec_custom(self, spec, data):
        msg = ""

        name = spec["name"]

        # Custom detector...
        detector = config['detector']
        method = detector['method']

        if hasattr(self, method):
            handler = getattr(self, method)
            df = handler(data)
        else:
            logger.exception(
                f"No method defined to detect changepoints",
                extra={"transform": self.name, "data": json.dumps(detector, indent=4)}
            )
            df = None

        return df

    def process_spec_default(self, spec, data):
        """
        Run the default change point detection
        """

        ## note: we need to save viz objects immediately after creation
        ## or they will be overwritten when the next viz object is created

        msg = ""
        name = spec['name']

        indicator_ts = data['indicator']
        cpd = self.run_changepoint_detector(indicator_ts, name)
        changepoints = cpd['changepoints']

        # save changepoint visualization
        viz = cpd['viz']
        filename = f"{name}-changepoints.png"
        l_msg = self.store_viz(spec, filename, viz)
        msg += l_msg
        cpd.pop('viz', None)

        observations = {}
        for observation, observation_ts in data['observations'].items():
            regimes = self.compute_regimes(indicator_ts, observation_ts, changepoints)
            viz = self.visualize_regimes(observation_ts, regimes)
            observations[observation] = {
                "regimes": regimes,
                "viz": viz
            }
            # save regimes visualization
            filename = f"{name}-regime-{observation}.png"
            l_msg = self.store_viz(spec, filename, viz)
            msg += l_msg
            observations[observation].pop('viz', None)

        logger.debug(
            f"Saved visualizations",
            extra={"transform": self.name, "data": msg}
        )

        result = {
            "changepoints": cpd,
            "observations": observations
        }

        return result


    def run_changepoint_detector(self, df, name):
        # init the change point detector object
        cpd_obj = BaseChangePointDetectorModel(df)

        # run the change point detection algorithm
        changepoints = cpd_obj.detect_changepoints(method="hybrid")

        # get the viz
        viz = cpd_obj.visualize_changepoints(df, changepoints, name)

        cpd = {
            "changepoints": changepoints,
            "viz": viz
        }

        return cpd

    def fit_project_linear_regression(self, y):
        x = np.array(range(0, len(y)))
        y_min = min(y)

        # shift to bring y_min to 0
        ynorm = (y - y_min)

        # fit the polynomial and compute coefficients
        z = np.polyfit(x, ynorm, 1)

        # get the projection as per the fit to data
        y_proj = np.polyval(z, len(y)-1) + y_min

        return y_proj

    def compute_impact_factor(self, data, start, end):
        y = data[start:end]
        y_mean = np.mean(y)

        y_proj = self.fit_project_linear_regression(y)

        # expected lift factor
        lfactor_EXP = y_proj/y_mean

        # observed lift factor
        lfactor_OBS = data[end]/y_mean

        # impact
        if lfactor_EXP < 1 and lfactor_OBS < 1:
            impact = (lfactor_EXP) / (lfactor_OBS)
        elif lfactor_EXP == 1:
            impact = 0   # If the expected lift factor is 1 i.e there is no change before and after cp, impact is 0
        else:
            impact = (lfactor_OBS-1) / (lfactor_EXP-1)

        direction = lfactor_OBS / lfactor_EXP
        if direction < 1 and impact != 0 :
            impact = 1 / impact

        return abs(impact)


    def compute_regimes(self, indicator_ts, observation_ts, changepoints):
        short_regime_range = 7
        damping = 0.1
        max_cap_factor = 1.5

        dates = observation_ts.index.values
        indicator_ts = indicator_ts.values
        observation_ts = observation_ts.values

        changepoint_indxs = [0] + changepoints

        regime_data = []
        for i in range(0, len(changepoint_indxs)-2):
            ## compute the expected impact to value in the next regime

            # get start and end indices for current regime
            start = changepoint_indxs[i]
            end = changepoint_indxs[i+1]

            # get prev regime start indices
            prev_start = changepoint_indxs[max(i-1,0)]

            # project what the ts value could have been at the end of current regime
            ts_values = observation_ts[start:end]
            ts_values_proj = self.fit_project_linear_regression(ts_values)

            # compute the impact factor at the change point for current regime
            impact_factor = self.compute_impact_factor(indicator_ts, start, end)

            # cmopute the caution indicator
            caution = self.compute_caution(impact_factor)

            # if very short current regime use prev two regimes
            if end-start <= short_regime_range:
                start = prev_start
                ts_values = observation_ts[start:end]

            # get the ts values over last 30 day time period to account for month-end highs
            ts_values_month = observation_ts[max(0,end-30):end]

            # get prev, next regime dates
            next_regime_dates = dates[changepoint_indxs[i+1]:changepoint_indxs[i+2]]
            prev_regime_dates = dates[start:end]
            prev_regime_len   = len(prev_regime_dates)-1


            # compute potential max ts value in the next regime
            if impact_factor >= 1:
                m1 = max(ts_values)
                m2 = min(ts_values_proj*math.sqrt(impact_factor), max(ts_values)*(impact_factor**damping))
                m3 = min(np.median(ts_values)*math.sqrt(impact_factor), max(ts_values)*(impact_factor**damping))
                max_ts_values = [round(x) for x in sorted([m1, m2, m3], reverse=True)]
                if caution == 'low':
                    max_cap = np.median(ts_values) * max_cap_factor
                    max_ts_values = [round(min(x, max_cap)) for x in max_ts_values]
                # we have to consider the last month high
                max_ts_values = sorted(max_ts_values + [round(max(ts_values_month))], reverse=True)[0:3]

                min_ts_values = [round(x) for x in sorted([min(ts_values), min(ts_values), min(ts_values)])]
            else:
                max_ts_values = [round(x) for x in sorted([max(ts_values), max(ts_values), max(ts_values)])]

                m1 = min(ts_values_month) #min(ts_values)
                m2 = ts_values_proj * math.sqrt(impact_factor)
                m3 = np.mean(ts_values) * math.sqrt(impact_factor)
                min_ts_values = [round(x) for x in sorted([m1, m2, m3])]

            # generate the context string
            rd = {
                "start_date": next_regime_dates[0],
                "end_date": next_regime_dates[-1],
                "prev_regime_start_date": prev_regime_dates[0],
                "prev_regime_end_date": prev_regime_dates[-1],
                "impact_factor": impact_factor,
                "min_value": min_ts_values,
                "max_value": max_ts_values,
                "prev_max_value": max(ts_values),
            }
            context = self.generate_regime_context(rd)
            rd['context'] = context

            regime_data.append(rd)

        # add the special case of final regime
        context = self.generate_regime_context(rd, final_rec=True)
        rd['context'] = context
        regime_data[-1] = rd

        return regime_data

    def compute_caution(self, impact_factor):
        caution = 'low'
        if impact_factor > 4 and impact_factor <= 6:
            caution = "medium"
        if impact_factor > 6:
            caution = "high"
        return caution


    def generate_regime_context(self, rd, final_rec=False):

        def millify(n):
            n = float(n)
            millnames = ['','K','M','B']
            millidx = max(0,min(len(millnames)-1,
                                int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
            return str(round(n / 10**(3 * millidx), 2)) + str(millnames[millidx])

        impact_factor = rd['impact_factor']
        caution = self.compute_caution(impact_factor)

        if caution == 'low':
            high_str = f"around ${millify(rd['max_value'][0])}"
        if caution == 'medium':
            high_str = f"between ${millify(rd['max_value'][1])} and ${millify(rd['max_value'][0])}"
        if caution == 'high':
            high_str = f"between ${millify(rd['max_value'][2])} and ${millify(rd['max_value'][1])} in the near future"

        multiple_str = round(rd['max_value'][0] / rd['prev_max_value'], 2)

        regime_start_date       = pd.to_datetime(str(rd['start_date'])).strftime("%-d %B, %Y")
        prev_regime_start_date  = pd.to_datetime(str(rd['prev_regime_start_date'])).strftime("%-d %B, %Y")
        prev_regime_end_date    = pd.to_datetime(str(rd['prev_regime_end_date'])).strftime("%-d %B, %Y")

        context = [f"{regime_start_date}: Regime change detected."] + \
                    [f"Expecting {self.cautions[caution]['desc']} change in spikiness from previous regime spanning {prev_regime_start_date} to {prev_regime_end_date}."] + \
                    [f"Recommendation 1: Expect highs around {multiple_str}x of previous regime high."] + \
                    [f"Recommendation 2: Expect highs {high_str}."]

        if final_rec:
            context[1] = f"{self.cautions[caution]['rec']}"

        return " ".join(context)


    def visualize_regimes(self, observation_ts, regime_data):
        fig, ax = plt.subplots(figsize=(15, 7))

        ax.plot_date(observation_ts.index, observation_ts.values,
                     linestyle='-', marker='')

        markers = {
            "^": {"color": "blue"},
            "v": {"color": "red"},
        }

        max_ts_value = 0
        sgn = 1

        # for each regime to visualize
        for rd in regime_data:

            impact_factor = rd['impact_factor']
            x = mdates.date2num(rd['start_date'])

            caution = self.compute_caution(impact_factor)

            # Create rectangle patches for the projection bands
            for i in range(0, len(rd['max_value'])):
                height = rd['max_value'][i]-rd['min_value'][i]
                rect = Rectangle((x, rd['min_value'][i]),
                                 width=mdates.date2num(rd['end_date'])-mdates.date2num(rd['start_date']),
                                 height=height,
                                 linewidth=1,
                                 edgecolor='r',
                                 facecolor=self.cautions[caution]['color'],
                                 alpha=0.1)

                # Add the patch to the Axes
                ax.add_patch(rect)

                # check for exit
                if caution == 'low' and i == 0:
                    break
                if caution == 'medium' and i == 1:
                    break

            # add a vertical line for the regime boundary
            ax.axvline(x,
                       linestyle='--',
                       color='black')

            dt = pd.to_datetime(str(rd['start_date'])).strftime("%Y-%m-%d")
            y = observation_ts[observation_ts.index==dt].values[0]
            regime_start_date = pd.to_datetime(str(rd['start_date'])).strftime("%-d %B, %Y")
            ax.annotate(regime_start_date,
                        (x, y),
                        xytext=(2, sgn*15),
                        xycoords='data',
                        textcoords='offset points',
                        bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.75))

            marker = '^' if impact_factor >= 1 else 'v'
            ax.plot(x, y,
                    marker=marker,
                    color=markers[marker]['color'],
                    markersize=12)

            # tracking vars
            max_ts_value = max_ts_value if max(rd['max_value'])<max_ts_value else max(rd['max_value'])
            sgn *= -1

        ax.set_ylim(bottom=0, top=max_ts_value)
        ax.set_ylabel('Value')
        ax.set_title('Projected Regime Bands')

        fig.autofmt_xdate()
        return plt


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

        # first, check if we need to store locally
        if self.args.get('testmode', False):

            outputpath = self.args['test_outpath']
            try:
                os.makedirs(outputpath)
            except:
                pass

            testplotfile = os.path.join(outputpath, filename)
            viz.savefig(testplotfile)

            msg += f"Stored (local): {testplotfile}" + "\n"

        # write to s3
        # where are we storing it?
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

        resultfile = os.path.join(targetdir, f"data.json")
        metadatafile = os.path.join(targetdir, f"metadata.json")

        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec

        # write to s3
        with s3.open(resultfile, 'w') as fd:
            json.dump(result, fd, indent=4, cls=SafeEncoder)
        with s3.open(metadatafile, 'w') as fd:
            json.dump(metadata, fd, indent=4, cls=SafeEncoder)

        msg = f"s3 location: {resultfile}" + "\n"
        msg += f"metadata location: {metadatafile}" + "\n"

        logger.debug(f"Wrote change point result to S3",
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


    def get_datewindow(self, source, spec):
        datewindow = {}
        default_delta = 180

        start_date_str = source.get('start_date')
        end_date_str = source.get('end_date')

        if not end_date_str:
            logger.debug(f"end date not specified in {spec['name']}. Using default as yesterday's date.")
            end  = self.args['run_date'] # yesterday
            end_date_str = end.isoformat()

        if not start_date_str:
            logger.debug(f"start date not specified in {spec['name']}. Using default as 180 days prior to end date. ")
            start = dateparser.parse(end_date_str).date() + timedelta(days=-default_delta)
            start_date_str = start.isoformat()

       # If start and end dates are specified, check if date is parseable
        try:
            start_date = dateparser.parse(start_date_str).date()
            end_date = dateparser.parse(end_date_str).date()
        except:
            logger.exception(
                        f"Invalid start date or end date. Skipping the spec {spec['name']}.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
            datewindow = None # be explicit
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
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.changepoint")
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

            for f in ["source", "detector"]:
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
            source = config['source']
            for f in ["indicator", "observations"]:
                if f not in source:
                    logger.exception(
                        f"Spec config has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            # expections have occured. continue to next spec
            if do_process_spec == False:
                continue

            # get time_window for indicator and observation data set
            datewindow = self.get_datewindow(source, spec)
            if datewindow is None :
                do_process_spec = False
                continue

            # first, load the indicator dataset
            data = {}
            data['indicator'] = self.load_dataset(spec, 'indicator', source['indicator'], datewindow)
            if data['indicator'] is None:
                do_process_spec = False
                continue

            # then, load all the observations datasets
            data['observations'] = {}
            for ob_dataset, dataset in source['observations'].items():
                data['observations'][ob_dataset] = self.load_dataset(spec, ob_dataset, dataset, datewindow)

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
