import os
import io
import re
import json
import numpy as np
import pandas as pd
import time
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
from scipy.spatial import distance
import seaborn as sns
import matplotlib.pyplot as plt
import logging

from pandas.api.types import is_numeric_dtype

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.datasets import TransformDoodle
from enrichsdk.datasets import DynamicCustomDataset
from enrichsdk.utils import SafeEncoder

logger = logging.getLogger("app")


class AnomaliesBase(Compute):
    """
    Compute anomalies given a dataframe with columns

    Features of transform baseclass include:

        * Flexible configuration
        * Highlevel specification of columns combinations and detection strategy

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "AnomaliesBase"
        self.description = "Compute anomalies in column(s) of a dataframe"
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

    def get_profile(self):
        """
        Read the profile json from API
        """

        if (not hasattr(self, "args")):
            raise Exception(
                "'args' transform attribute should be defined to use default get_profile method"
            )
        for p in ['apicred']:
            if self.args.get(p) == None:
                raise Exception(
                    f"'{p}' attribute in args should be defined to use default get_profile method"
                    )

        # call the API to get the anomaly specs
        anomalyspecs, is_valid, msg = load_profile_api(self.args)
        logger.debug(
            f"Loading profile from API",
            extra={"transform": self.name, "data": msg},
        )
        if is_valid == False:
            raise Exception(f"Error loading profile")

        specs = anomalyspecs["specs"]
        logger.debug(
            f"Found {len(specs)} specs",
            extra={"transform": self.name, "data": json.dumps(anomalyspecs, indent=4)},
        )

        return anomalyspecs

    def get_specs(self, profile):
        if (not isinstance(profile, dict)) or ("specs" not in profile):
            raise Exception("Specs not defined in profile")
        return profile["specs"]

    def preprocess_spec(self, spec):
        '''
        to be overloaded in the derived class
        '''
        return spec

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
        handlers = self.get_handlers(spec)

        # use the specified strategy to detect anomalies
        try:
            strategy = config.get("strategy")
            if strategy == None:
                # We are doing the default anomaly detection which is deviation from mean
                data = self.process_spec_default(data, spec)
            elif strategy == "custom":
                # Custom callback
                data  = self.process_spec_custom(data, spec)
            else:
                # for now, we fallback to the default strategy
                data  = self.process_spec_default(data, spec)

            # The spec processor can return multiple dataframes
            if isinstance(data, pd.DataFrame):
                data = {name: data, "stats": {}}
        except:
            logger.exception(f"Failed to process {name}",
                             extra={
                                 'transform': self.name,
                                 'data': msg
                             })

            return None

        logger.debug(
            f"Processed anomalies",
            extra={"transform": self.name, "data": msg}
        )

        return data

    def process_spec_custom(self, datasets, profile, spec):
        msg = ""

        name = spec["name"]
        handlers = self.get_handlers(profile)

        # Custom...
        generate = spec["generate"]
        callback = None
        if (generate in handlers) and (not callable(handlers[generate])):
            callback = handlers[generate]
        elif hasattr(self, generate):
            callback = getattr(self, generate)

        if callback is None:
            raise Exception(f"[{name}] Invalid callback: {generate}")

        # Get hold of the data first...
        sources = self.get_spec_sources(spec, datasets)

        return callback(sources, spec)

    def process_spec_default(self, data, spec):
        """
        Handle one specification at a time..
        """

        partialsamplerate = 0.05
        samplerate_lut = {
            "all": 1.0,
            "partial": partialsamplerate,
            "none": 0.0
        }
        tolerances = {
            "low": 1,
            "medium": 2,
            "high": 3,
        }

        def anomaly_note(row, threshold):
            distance = row[f"__anomaly_distance__"]
            if distance > threshold:
                return f"{(round(distance/threshold,2))}x outside expected sample deviation"
            return f"within expected sample deviation"


        msg = ""
        msg += f"Using default centroid distance anomaly detector" + "\n"

        config = spec["config"]
        msg += f"Config: {json.dumps(config, indent=4)}" + "\n"

        # Get hold of the data first...
        name = spec["name"]
        orig_df = data
        total_samples = len(orig_df)

        metrics     = config.get("metrics", orig_df.columns)
        groups      = config.get('groups', [])
        outputs     = config.get("outputs", orig_df.columns)
        dimensions  = config.get("dimensions", orig_df.columns)
        columns     = list(set(metrics + outputs + dimensions))

        msg += f"Combined set of columns: {columns}" + "\n"
        msg += f"{note(orig_df, 'Original DF')}" + "\n"

        #########
        # default anomaly detection
        #########
        # get tolerance thresold
        tolerance = config.get("threshold", config.get("thresold", "medium"))
        scalefactor = tolerances.get(tolerance, 2)

        # get the sample strategy for the normal data
        normal_samples = config.get("normal_samples", "partial")
        samplerate = samplerate_lut[normal_samples]

        msg += f"(tolerance, scalefactor): ({tolerance}, {scalefactor})" + "\n"

        logger.debug(f"Setting up for spec: {spec['name']}",
                         extra={
                             'transform': self.name,
                             'data': msg
                         })

        anomaly_stats = {}
        plotdata = {}
        dfs = []

        #########
        # we first do the leaf level, per metric to check for anomalies
        #########
        msg = f"Processing metrics: {metrics}" + "\n\n"

        for metric in metrics:

            # make a copy of the df, we'll keep adding anomlay metrics to it
            df = orig_df[columns].copy()

            if not is_numeric_dtype(df[metric]):
                msg += f"{metric} Metric not numeric. Skipping\n"
                continue

            # compute the anomalies for this metric
            points      = df[metric].to_numpy()     # all data as an MxN matrix
            centroid    = df[metric].mean()          # the computed centroid of the dataset
            distances   = abs(points - centroid)    # distances of each point to centroid
            stddev      = np.nanstd(points)      # std dev of distances
            threshold   = stddev * scalefactor
            anomalies   = np.where(distances.flatten()>threshold, 'anomaly', 'normal')    # flag where anomalies occur

            # add columns indicating anomaly label
            id = f"metric-{metric}"
            df['id'] = id
            df['level'] = 'metric'
            df['name'] = metric
            df['__is_anomaly__'] = pd.Series(anomalies)

            # add columns indicating reason for anomaly
            df[f"__anomaly_distance__"] = pd.Series(distances.flatten())
            df[f"__anomaly_note__"] = df.apply(lambda x: anomaly_note(x, threshold), axis=1)

            df_a = df[df['__is_anomaly__']=='anomaly']
            n_anomalies = len(df_a)
            perc_anomalies = round(n_anomalies/total_samples*100, 2)

            df_n = df[df['__is_anomaly__']=='normal'].sample(frac=samplerate)
            df_n = df_n[0:min(3*n_anomalies,len(df_n))] # min 3x n_anomalies or configured sample of normal samples
            n_nsamples = len(df_n)

            # for this metric, we now have all the detected anomalies and the sampled normal data
            sampled_df = pd.concat([df_a, df_n])

            msg += f"--------------------------" + "\n"
            msg += f"Metric: {metric}" + "\n"
            msg += f"Computed stddev: {stddev}" + "\n"
            msg += f"Threshold: {threshold}" + "\n"
            msg += f"Anomalies: {n_anomalies}/{total_samples}={perc_anomalies}%" + "\n"
            msg += f"--------------------------" + "\n\n"

            anomaly_stats[id] = {
                "level": 'metric',
                "name": metric,
                "dimensions": dimensions,
                "n_anomalies": n_anomalies,
                "perc_anomalies": perc_anomalies,
                "n_normalsamples": n_nsamples,
                "n_plotsamples": len(df),
            }
            plotdata[id] = df

            dfs.append(sampled_df)

        logger.debug(f"Processed metrics level: {spec['name']}",
                         extra={
                             'transform': self.name,
                             'data': msg
                         })


        # #########
        # # then we do the group level, hierarchial
        # #########
        msg = f"Processing groups: {groups}" + "\n\n"

        for group in groups:
            group_name      = group.get('group')
            g_dimensions    = group.get('dimensions', dimensions)
            g_metrics       = group.get('metrics')

            # we don't have what we need, skip
            if group_name == None or metrics == None:
                continue

            if not all([is_numeric_dtype(df[metric]) for metric in g_metrics]):
                msg += f"{group_name} One or more metrics are not numeric\n"
                continue

            # make a copy of the df, we'll keep adding anomlay metrics to it
            df = orig_df[columns].copy()

            points      = df[g_metrics].to_numpy()    # all data as an MxN matrix
            centroid    = df[g_metrics].mean().values # the computed centroid of the dataset
            distances   = distance.cdist(points, np.array([centroid]), 'euclidean') # distances of each point to centroid
            distances   = np.reshape(distances, len(distances))
            stddev      = np.nanstd(points)         # std dev of distances
            threshold   = stddev * scalefactor
            anomalies   = np.where(distances.flatten()>threshold, 'anomaly', 'normal')    # flag where anomalies occur

            # add columns indicating anomaly label
            id = f"group-{group_name}"
            df['id'] = id
            df['level'] = 'group'
            df['name'] = group_name
            df['__is_anomaly__'] = pd.Series(anomalies)

            # add columns indicating reason for anomaly
            df[f"__anomaly_distance__"] = pd.Series(distances.flatten())
            df[f"__anomaly_note__"] = df.apply(lambda x: anomaly_note(x, threshold), axis=1)

            df_a = df[df['__is_anomaly__']=='anomaly']
            n_anomalies = len(df_a)
            perc_anomalies = round(n_anomalies/total_samples*100, 2)

            df_n = df[df['__is_anomaly__']=='normal'].sample(frac=samplerate)
            df_n = df_n[0:min(3*n_anomalies,len(df_n))] # min 3x n_anomalies or configured sample of normal samples
            n_nsamples = len(df_n)

            # for this metric, we now have all the detected anomalies and the sampled normal data
            sampled_df = pd.concat([df_a, df_n])

            msg += f"--------------------------" + "\n"
            msg += f"Group: {group_name}" + "\n"
            msg += f"Computed stddev: {stddev}" + "\n"
            msg += f"Threshold: {threshold}" + "\n"
            msg += f"Anomalies: {n_anomalies}/{total_samples}={perc_anomalies}%" + "\n"
            msg += f"--------------------------" + "\n"

            anomaly_stats[id] = {
                "level": 'group',
                "name": group_name,
                "metrics": g_metrics,
                "dimensions": g_dimensions,
                "threshold": threshold,
                "n_anomalies": n_anomalies,
                "perc_anomalies": perc_anomalies,
                "n_normalsamples": n_nsamples,
                "n_plotsamples": len(df),
            }
            plotdata[id] = df

            dfs.append(sampled_df)

        logger.debug(f"Processed groups level: {spec['name']}",
                         extra={
                             'transform': self.name,
                             'data': msg
                         })

        if len(dfs) == 0:
            logger.debug(f"{name}: No outputs computed",
                         extra={
                             'transform': self.name,
                             'data': msg
                         })
            return None

        #########
        # construct the DF for output
        #########
        # concat for all metrics+groups
        df = pd.concat(dfs)
        # reorder columns
        first_cols = ['id', 'level', 'name']
        cols = first_cols + [c for c in df.columns if c not in first_cols]
        df = df[cols]

        msg = f"Final columns: {df.columns}" + "\n"

        window, start_date, end_date = self.get_window_dates(config, self.args)

        # compute stats of interest
        stats = {
            "timestamp": f"{datetime.now().isoformat()}",
            "policy": config,
            "data_start_date": f"{start_date}",
            "data_end_date": f"{end_date}",
            "strategy": "centroid",
            "tolerance": tolerance,
            "scalefactor": scalefactor,
            "normalsamples": normal_samples,
            "samplerate": samplerate,
            "n_rows": total_samples,
            "anomaly_stats": anomaly_stats,
        }

        msg += f"Stats: {json.dumps(stats, indent=4)}" + "\n"

        msg += f"{note(df, 'Anomaly DF')}" + "\n"

        logger.debug(f"Completed spec: {spec['name']}",
                         extra={
                             'transform': self.name,
                             'data': msg
                         })

        return {name: df, "stats": stats, "plotdata": plotdata}

    def summarize_dimension(self, df, d):
        col = '__is_anomaly__'
        max_cats = 10

        # first get the category labels for anomalies, we need to retain these
        anomaly_cats = list(set(df[df[col]=='anomaly'][d].values))

        # remove these rows, so they don't interfere in the next steps
        _df = df[df[col]!='anomaly'].copy()

        # determine how many topk categories to keep
        # if we already have too many categories from the anomaly rows
        # this will be 0
        topk = max(max_cats - len(anomaly_cats), 0)

        # then, get the top-K represented categories
        topk_cats = _df[[d]+[col]] \
                    .groupby(by=[d]) \
                    .agg('count') \
                    .sort_values(by=col, ascending=False) \
                    .head(topk) \
                    .reset_index()[d] \
                    .tolist()

        # what categoeies are we retaining
        retain_cats = anomaly_cats + topk_cats

        # label every other category as OTHER
        df[d] = df.apply(lambda x: 'OTHER' if x[d] not in retain_cats else x[d],
                        axis=1)

        return df


    def read_db_source(self, source):

        # Get the SQLAlchemy URI
        uri = self.get_db_uri(source)

        # Get the query
        query = self.get_db_query(source)

        # Create the engine
        engine = create_engine(uri)

        # Run the query
        df = pd.read_sql_query(satext(query), con=engine)

        # Now the input load...
        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "database",
                    "nature": "input",
                    "objects": [self.get_printable_db_uri(uri)],
                },
            ],
        }

        self.update_frame(source, f"Dataset: {dataset}", df, lineage)

        return df

    def read_s3_data(self, filename, params={}):
        # assume we have a resolved s3fs object
        s3 = self.args['s3']
        if s3.exists(filename):
            df = pd.read_csv(s3.open(filename), **params)
            return df
        return None

    def get_spec_sources(self, spec, datasets):

        name = spec["name"]

        if ("sources" not in spec) and ("source" not in spec):
            raise Exception(f"[{name}] Invalid specification. Missing dataset")

        sources = spec.get("sources", spec.get("source"))
        if isinstance(sources, str):
            sources = [sources]

        policy = spec.get("missing", "fail")
        for s in sources:
            if s not in datasets:
                if policy == "fail":
                    raise Exception(f"[{name}] Missing source: {s}")

        return {s: datasets[s] for s in sources if s in datasets}

    def update_frame(self, source, description, df, lineage=None):

        if isinstance(source, str):
            name = source
            description = ""
        else:
            name = source["name"]
            description = source.get("description", "")

        if self.state.has_frame(name):
            return

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

    def load_dataset(self, spec):
        name        = spec['name']
        config      = spec['config']

        source_name = config['dataset']
        source_id   = config['source_id']
        source_version = config.get('source_version', 'v1')
        dataset     = config['dataset']

        datacred = self.args['datacred']
        doodle = TransformDoodle(self, self.state, datacred)

        #=> the source may have a different id than source_id
        # because we gave both the name and the id
        source, paths = doodle.get_source_paths(start=datetime.today(), # + timedelta(days=-7),
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

    def get_window_dates(self, config, args):
        # get the window size
        window = config.get("window")
        if window == None or window == "":
            window = "1"
        try:
            window = int(window)
        except:
            raise Exception(
                "window param in config needs to be a string integer"
            )

        # determine start and end dates for dataset
        end_date = args["run_date"]
        start_date = end_date + timedelta(days=-window+1)

        return window, start_date, end_date


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

    def save_image(self, fig, plotfile, testplotfile):
        s3 = self.args['s3']

        # save locally when testing
        if self.args.get('testmode', False):
            outputpath = self.args['test_outpath']
            try:
                os.makedirs(outputpath)
            except:
                pass
            testplotfile = os.path.join(outputpath, testplotfile)
            fig.savefig(testplotfile)

        # write to s3
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png')
        img_data.seek(0)
        with s3.open(plotfile, 'wb') as fd:
            fd.write(img_data.getbuffer())


    def s3_store_result(self, spec, data):
        name        = spec['name']
        appname     = spec.get('app','common')
        namespace   = spec.get('namespace', 'default')
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()

        config      = spec["config"]

        # get the dataframe and
        # add additional columns
        df = data[name]
        df["__run_date__"] = run_date

        # get the stats object
        stats = data["stats"]
        plotdata = data["plotdata"]

        # where are we storing it?
        targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")

        anomaliesfile   = os.path.join(targetdir, f"outliers.csv")
        statsfile       = os.path.join(targetdir, f"stats.json")
        metadatafile    = os.path.join(targetdir, f"metadata.json")

        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec

        ## plot the results
        msg = note(df, f"{name} - Anomalies Tagged") + "\n"
        msg += f"Anomalies: {anomaliesfile}" + "\n"
        msg += f"Stats: {statsfile}" + "\n"

        # for each level-name combination (indexed by id)
        for id in set(df['id'].values):

            data_df = plotdata[id]
            data_df = data_df.reset_index(drop=True)

            # Plot the data
            if stats['anomaly_stats'][id]['level'] == 'metric':
                # for the metrics level
                x = stats['anomaly_stats'][id]['name']
                dimensions = stats['anomaly_stats'][id]['dimensions']
                plot = sns.displot(data_df,
                                    x=x,
                                    hue="__is_anomaly__",
                                    stat="probability",
                                    bins=100)
                plot.fig.subplots_adjust(top=.95)
                plot.set(title=f'Metric Distribution ({id})')
                fig = plot.fig
                testplotfile = f'{name}-{id}.png'
                plotfile = os.path.join(targetdir, f"plot-{id}.png")
                msg += f"plot: {plotfile}" + "\n"
                self.save_image(fig, plotfile, testplotfile)

                # for each dimension, we show a categorical plot
                for d in dimensions:
                    if data_df[d].dtype not in ['O', 'string', 'str']:
                        # pass if numeric type
                        continue
                    m_data_df = data_df[[d]+[x]+['__is_anomaly__']] # keep only the columns we need
                    m_data_df = self.summarize_dimension(data_df, d)
                    plot = sns.catplot(
                                data=m_data_df, kind="strip",
                                x=x, y=d, hue="__is_anomaly__")
                    plot.fig.subplots_adjust(top=.95)
                    plot.set(title=f'Distribution of {d} ({id})')
                    fig = plot.fig
                    testplotfile = f'{name}-{id}-dimension-{d}.png'
                    plotfile = os.path.join(targetdir, f"plot-{id}-dimension-{d}.png")
                    msg += f"plot: {plotfile}" + "\n"
                    self.save_image(fig, plotfile, testplotfile)

            else:
                # for the groups level
                metrics = stats['anomaly_stats'][id]['metrics']
                dimensions = stats['anomaly_stats'][id]['dimensions']
                data_df = data_df[dimensions+metrics+['__is_anomaly__']]  # only retain the columns we need
                plot = sns.pairplot(data_df,
                                    hue='__is_anomaly__')
                plot.fig.subplots_adjust(top=.95)
                plot.fig.suptitle(f'Pairplot Structure ({id})')
                fig = plot.fig

                testplotfile = f'{name}-{id}.png'
                plotfile = os.path.join(targetdir, f"plot-{id}.png")
                msg += f"plot: {plotfile}" + "\n"
                self.save_image(fig, plotfile, testplotfile)


        # write data to s3
        with s3.open(anomaliesfile, 'w') as fd:
            df.to_csv(fd, index=False)
        with s3.open(statsfile, 'w') as fd:
            json.dump(stats, fd, indent=4, cls=SafeEncoder)
        with s3.open(metadatafile, 'w') as fd:
            json.dump(metadata, fd, indent=4, cls=SafeEncoder)

        logger.debug("Wrote anomalies".format(name),
                        extra={"transform": self.name,
                                "data": msg})

    def store_result(self, spec, data):
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
            self.s3_store_result(spec, data)
        elif sink == "db":
            # store in db
            self.db_store_result(spec, data)
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the anomaly profile
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.outliersv2")
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

        # Now go through each spec and generate anomaly reports
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

            for f in ["source_id"]:
                if f not in config:
                    logger.exception(
                        f"Spec config has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break

            if not do_process_spec:
                continue

            ## pre-process the spec
            try:
                spec = self.preprocess_spec(spec)
                logger.debug(f"Preproccessed spec: {spec['name']}",
                             extra={
                                 'transform': self.name,
                                 'data': json.dumps(spec, indent=4)
                             })

                ## we can now proceed with processing the spec
                # frist, load the source data
                data = self.load_dataset(spec)

                ## process the spec to detect outliers
                data = self.process_spec(spec, data)

                if ((not isinstance(data, dict)) or
                    (len(data) == 0)):
                    continue

                # write the detected outliers
                self.store_result(spec, data)
            except:
                logger.exception(f"Failed to process {name}",
                                 extra={
                                     'transform': self.name
                                 })

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
