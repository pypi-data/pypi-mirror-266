import io
import os
import sys
import json
import time
import base64
import random
import logging
import hashlib
import traceback
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from enrichsdk import Compute, S3Mixin, EmailMixin
from enrichsdk.utils import note, SafeEncoder

from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import RocCurveDisplay, auc, roc_curve

from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.pipeline import make_pipeline

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.datasets import TransformDoodle

from dateutil import parser as dateparser

sns.set_context("notebook")

logger = logging.getLogger("app")

class ClassifierBase(Compute):
    """
    Take a training dataset and one or more eval datasets
    Builds a classification model using the training dataset
    Applies the model on the eval dataset(s) and generates predictions

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of steps in ML classification flow:
            * specify multiple datasets (one for training, one or more for evaluation)
            * specify optional dataset prep methods
            * specify training model details with support for imbalanced datasets
            * specify evaluation strategy on one or more datasets
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "ClassifierBase"
        self.description = "Classification of data using a trained ML model"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
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

    def update_state(self, name, df, description, dependencies=[]):

        # append the existing dataframe if it exists
        if self.state.has_frame(name):
            frame = self.state.get_frame(name)
            df = pd.concat([df, frame['df']], ignore_index=True)

        updated_detail = {
            'df': df,
            'description': description,
            'transform': self.name,
            'frametype': 'pandas',
            'params': self.get_column_params(name, df) + dependencies
        }

        self.state.update_frame(name, updated_detail, create=True)


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

    def store_viz(self, spec, filename, viz, s3store=False):
        appname     = spec.get('app', self.name)
        name        = spec['name']
        namespace   = spec.get('namespace', 'default')

        msg = ""

        # store locally
        outputpath = os.path.join(self.args['output'], name)
        try:
            os.makedirs(outputpath)
        except:
            pass
        testplotfile = os.path.join(outputpath, f"{filename}")
        viz.savefig(testplotfile)
        msg += f"Stored (local): {testplotfile}" + "\n"

        # base64 encode the image
        img_data = io.BytesIO()
        viz.savefig(img_data, format='png')
        img_data.seek(0)
        img_data_b64 = base64.b64encode(img_data.read()).decode()

        # write to s3
        if s3store == True:
            # where are we storing it?
            run_date    = self.args['run_date']
            s3          = self.args['s3']
            epoch       = self.epoch
            targetdir   = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")
            vizfile     = os.path.join(targetdir, f"{filename}")

            img_data = io.BytesIO()
            viz.savefig(img_data, format='png')
            img_data.seek(0)
            with s3.open(vizfile, 'wb') as fd:
                fd.write(img_data.getbuffer())

            msg += f"Stored (remote): {vizfile}" + "\n"

        return msg

    def construct_result_metadata(self,):
        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec
        metadata['predictspec'] = predictspec
        metadata['result'] = result
        return metadata


    def s3_store_result(self, spec, predictspec, result, df):
        appname     = spec.get('app',self.name)
        name        = spec['name']
        namespace   = spec.get('namespace', 'default')
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = self.epoch

        # where are we storing it?
        targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")

        predictspecname = predictspec.get("name", "NO-NAME")
        csvfile = os.path.join(targetdir, f"{predictspecname}-data.csv")
        resultfile = os.path.join(targetdir, f"{predictspecname}-result.json")

        # write to s3
        with s3.open(csvfile, 'w') as fd:
            df.to_csv(fd, index=False)
        with s3.open(resultfile, 'w') as fd:
            json.dump(result, fd, indent=4, cls=SafeEncoder)

        msg = f"Storage: S3" + "\n"
        msg += f"data CSV location: {csvfile}" + "\n"
        msg += f"result location: {resultfile}" + "\n"

        logger.debug(f"Wrote classification result [{predictspecname}]",
                        extra={"transform": self.name,
                                "data": msg})

    def disk_store_result(self, spec, predictspec, result, df):
        name = spec['name']
        predictspecname = predictspec['name']
        outputpath = os.path.join(self.args['output'], f"{name}")
        try:
            os.makedirs(outputpath)
        except:
            pass
        csvfile = os.path.join(outputpath, f"{predictspecname}-data.csv")
        resultfile = os.path.join(outputpath, f"{predictspecname}-result.json")

        msg = f"Storage: Disk" + "\n"
        msg += f"data CSV location: {csvfile}" + "\n"
        msg += f"result location: {resultfile}" + "\n"

        df.to_csv(csvfile, index=False)
        with open(resultfile, 'w') as fd:
            json.dump(result, fd, indent=4, cls=SafeEncoder)

        logger.debug(f"Wrote classification result [{predictspecname}]",
                        extra={"transform": self.name,
                                "data": msg})


    def load_sources(self, profilespec):
        """
        Load all the data sources
        """
        data = {}

        for source in profilespec.get('sources', []):
            name = source.get('name', 'NOT_SPECIFIED')

            # check for all fields needed
            if any(p not in source for p in ['nature', 'name', 'filename', 'stage']):
                logger.error(f"Malformed source [{name}]",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': json.dumps(source, indent=4)
                             }))
                continue

            if source['nature'] == 'disk':
                filename = source['filename']
                filename = f"{self.args['root']}/{filename}"
                df = pd.read_csv(filename)
                if df is None:
                    logger.error(f"Source not found [{name}]",
                                 extra=self.config.get_extra({
                                     'transform': self.name,
                                     'data': json.dumps(source, indent=4)
                                 }))
                    continue

                data[name] = df

            else:
                continue

            self.update_state(name, df, f"Source: {name}")

        # we have loaded all available data sources
        return data

    def store_result_data(self, spec, predictspec, result, df):
        name = predictspec.get("name")
        store   = predictspec.get('store', ["disk"])

        if "s3" in store:
            # store in s3
            self.s3_store_result(spec, predictspec, result, df)
        if "db" in store:
            # store in db
            self.db_store_result(spec, predictspec, result, df)
        if "disk" in store:
            # store in disk
            self.disk_store_result(spec, predictspec, result, df)

        # => Document the state
        self.update_state(name, df, f"Predictions for {name}")

    def store_metadata(self, spec, results):
        """
        Store all the metadata for the full run
        """
        metadata = self.get_default_metadata(self.state)
        metadata['spec'] = spec
        metadata['results'] = results

        store = spec.get("store", ["disk"])

        if "s3" in store:
            # store in s3
            appname     = spec.get('app',self.name)
            name        = spec['name']
            namespace   = spec.get('namespace', 'default')
            run_date    = self.args['run_date']
            s3          = self.args['s3']
            epoch       = self.epoch

            # where are we storing it?
            targetdir = os.path.join(self.args['s3root'], f"{appname}/{namespace}/{name}/{run_date}/{epoch}")
            metadatafile = os.path.join(targetdir, f"metadata.json")

            # write to s3
            with s3.open(metadatafile, 'w') as fd:
                json.dump(metadata, fd, indent=4, cls=SafeEncoder)
        if "db" in store:
            # store in db
            self.db_store_metadata(spec, predictspec, result, df)
        if "disk" in store:
            # store in disk
            name = spec['name']
            outfile = os.path.join(self.args['output'], f"{name}/metadata.json")
            with open(outfile, 'w') as fd:
                fd.write(json.dumps(metadata,indent=4))


    ##################################################################
    # Data preparation
    ##################################################################
    def prep_data(self, profilespec, data, artifacts):
        """
        Do any data prep needed
        We may need to do data scaling, normalization, etc. here
        Any artifacts of the prep that will be needed by the
        prediction stage must be returned in this function
        """

        # setup the training data and artifacts
        train_data = None
        for source in profilespec['sources']:
            if source['stage'] == "train":
                train_data = source['name']
        if train_data == None:
            return data, artifacts

        # check if a prep data method is specified
        prep_data = profilespec.get("prep", {}).get("method")
        if prep_data == None:
            return data, artifacts

        # call the prep data method
        msg = ""
        if hasattr(self, prep_data):
            handler = getattr(self, prep_data)
            data[train_data], artifacts, msg = handler(data[train_data], artifacts, 'train')

        logger.debug(f"Prepped training data [{train_data}]",
                     extra=self.config.get_extra({
                         'transform': self.name,
                         'data': msg
                     }))

        return data, artifacts

    ##################################################################
    # Training and prediction functions
    ##################################################################
    def make_predictions(self, profilespec, data, classifiers, artifacts):
        """
        Generate predictions for the various eval datasets
        """

        # to collect all the results
        results = {}

        # for each prediction spec in the profilespec
        for spec in profilespec.get('predict', []):
            # process it
            name = spec['name']
            if spec.get('enable', True) == False:
                logger.error(f"Spec [{name}] disabled, skipping",
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                continue

            _dfs = []
            for source in spec.get('sources', []):
                _dfs.append(data[source])
            if len(_dfs)>0:
                eval_df = pd.concat(_dfs)
            else:
                logger.error(f"No sources to eval, skipping",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': json.dumps(spec, indent=4)
                             }))
                continue

            # get the target column name
            target = spec.get("target")
            ignore = spec.get("ignore", [])
            if target == None:
                logger.error(f"Target column not specified, skipping eval [{name}]",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': json.dumps(spec, indent=4)
                             }))
                continue

            # we now have eval_df
            # check if a prep data method is specified
            prep_data = profilespec.get("prep", {}).get("method")
            if prep_data != None:
                if hasattr(self, prep_data):
                    handler = getattr(self, prep_data)
                    prepped_eval_df, artifacts, msg = handler(eval_df, artifacts, 'predict')

                logger.debug(f"Prepped eval data [{name}]",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': msg
                             }))

            # check if all required columns are present
            missing_cols = set(artifacts['columns']).difference(set(prepped_eval_df.columns))
            for c in missing_cols:
                prepped_eval_df[c] = 0
            logger.debug(f"Added missing columns [{name}]",
                         extra=self.config.get_extra({
                             'transform': self.name,
                             'data': f"Missing cols: {missing_cols}"
                         }))


            # we now have the prepped eval df
            # run the specified classifier on it
            classifier_name = spec.get("model", "best")
            if classifier_name == "best":
                classifier_name = classifiers["best"]

            classifier = classifiers[classifier_name]['model']

            # create the data arrays
            X = prepped_eval_df[[c for c in prepped_eval_df.columns if c not in [target]+ignore]].to_numpy()

            # make the predictions
            r = classifier.predict(X)
            eval_df["__prediction"] = pd.Series(r)

            result = {
                "spec": spec,
                "n_datapoints": len(eval_df),
                "n_predictions": eval_df["__prediction"].value_counts().to_dict()
            }
            results[name] = result

            logger.debug(f"Predictions done [{name}]",
                         extra=self.config.get_extra({
                             'transform': self.name,
                             'data': note(eval_df, f"Predictions [{name}]")
                         }))

            # store results data csv
            self.store_result_data(profilespec, spec, result, eval_df)

        return results


    def get_classifier_pipeline(self, model):
        """
        Construct the classifier pipeline
            1. resampling
            2. classifier model
        """

        # do we need to resample the data
        # supports upsampling the minority class for now
        resample = model.get("resample")
        if resample == 'random':
            resampler = RandomOverSampler()
        elif resample == 'smote':
            resampler = SMOTE()
        else:
            # no resampling by default
            resampler = None

        # then get the classifier algorithm
        algorithm = model.get("model", {}).get("algorithm")
        params = model.get("model", {}).get("params", {})
        if algorithm == "knn":
            classifier = KNeighborsClassifier(**params)
        elif algorithm == "svm":
            classifier = svm.SVC(**params)
        else:
            # use the kNN algorithm by default
            classifier = KNeighborsClassifier(n_neighbors=3)

        # construct the pipeline
        if resampler == None:
            pipeline = classifier
        else:
            pipeline = make_pipeline(resampler, classifier)

        return pipeline

    def do_training(self, profilespec, modelspec, X, y, model, cv, metric):
        """
        Train a model given a dataset and a pipeline
        """

        msg = ""

        name = modelspec['name']

        tprs = []
        aucs = []
        mean_fpr = np.linspace(0, 1, 100)

        fig, ax = plt.subplots(figsize=(9, 9))
        for fold, (train, test) in enumerate(cv.split(X, y)):
            model.fit(X[train], y[train])
            viz = RocCurveDisplay.from_estimator(
                model,
                X[test],
                y[test],
                name=f"ROC fold {fold}",
                alpha=0.3,
                lw=1,
                ax=ax,
            )
            interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
            interp_tpr[0] = 0.0
            tprs.append(interp_tpr)
            aucs.append(viz.roc_auc)
        ax.plot([0, 1], [0, 1], "k--", label="chance level (AUC = 0.5)")

        # get the final model fit
        model.fit(X, y)

        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)
        ax.plot(
            mean_fpr,
            mean_tpr,
            color="b",
            label=r"Mean ROC (AUC = %0.2f $\pm$ %0.2f)" % (mean_auc, std_auc),
            lw=2,
            alpha=0.8,
        )

        std_tpr = np.std(tprs, axis=0)
        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
        ax.fill_between(
            mean_fpr,
            tprs_lower,
            tprs_upper,
            color="grey",
            alpha=0.2,
            label=r"$\pm$ 1 std. dev.",
        )

        ax.set(
            xlim=[-0.05, 1.05],
            ylim=[-0.05, 1.05],
            xlabel="False Positive Rate",
            ylabel="True Positive Rate",
            title=f"[{name}] Mean ROC curve with variability')",
        )
        ax.axis("square")
        ax.legend(loc="lower right", fontsize=16)
        plt.tight_layout()

        # save training visualization
        filename = f"train-{name}-roc.png"
        l_msg = self.store_viz(profilespec, filename, plt)

        msg += l_msg

        # return the appropriate metric
        if metric == "auc":
            metric_val = mean_auc
        elif metric == "tpr":
            metric_val = mean_tpr
        elif metric == "fpr":
            metric_val = mean_fpr
        else:
            metric_val = mean_auc

        classifier = {
            "model": model,
            "metric": metric_val
        }

        return classifier, msg

    def decide_best_classifier(self, classifiers):
        max_metric = 0
        for name, classifier in classifiers.items():
            if classifier['metric'] >= max_metric:
                best = name
                max_metric = classifier['metric']
        return best



    def train_models(self, profilespec, data):
        """
        Model training
        """
        msg = ""

        # prep the training data
        # and generate any artifacts needed later
        artifacts = {}
        data, artifacts = self.prep_data(profilespec, data, artifacts)
        # we need a list of all columns which will be used in training
        for source in profilespec['sources']:
            if source['stage'] == "train":
                train_data = source['name']
                artifacts['columns'] = list(data[train_data].columns)

        # required params
        trainspec = profilespec.get("train")
        metric  = trainspec.get("metric", "auc") #what is the metric against which to compare models
        folds   = trainspec.get("folds", 1)      #how many folds for cross validation

        classifiers = {}

        # for each model to train
        models = trainspec.get("models", [])
        for model in models:
            if model.get("enable", True) == False:
                continue

            name    = model.get("name", f"{hashlib.md5(json.dumps(model).encode('utf-8')).hexdigest()}")
            model['name'] = name
            dataset = model.get("source")
            target  = model.get("target")
            ignore  = model.get("ignore", [])

            if dataset == None or dataset not in data:
                logger.error(f"Dataset not known, skipping training [{name}]",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': json.dumps(model, indent=4)
                             }))
                continue
            if target == None:
                logger.error(f"Target column not specified, skipping training [{name}]",
                             extra=self.config.get_extra({
                                 'transform': self.name,
                                 'data': json.dumps(model, indent=4)
                             }))
                continue

            msg += f"Model: {name}" + "\n"
            msg += f"Dataset: {dataset}" + "\n"
            msg += f"Target column: {target}" + "\n"
            msg += f"Ignore columns: {ignore}" + "\n"

            df = data[dataset]

            # create the data arrays
            X = df[[c for c in df.columns if c not in [target]+ignore]].to_numpy()
            y = df[target].to_numpy()

            msg += f"Size (X): {X.size}" + "\n"
            msg += f"Size (y): {y.size}" + "\n"

            # figure out the minority class
            # in case we need to resample
            class_distribution = pd.Series(y).value_counts(normalize=True)
            pos_label = class_distribution.idxmin()
            msg += f"Positive label: {pos_label}" + "\n"

            # construct the classifier pipeline object
            classifier_pipeline = self.get_classifier_pipeline(model)

            # set up the n-fold cross validation
            cv = StratifiedKFold(n_splits=folds)

            # do model training
            classifiers[name], l_msg = self.do_training(profilespec, model, X, y, classifier_pipeline, cv, metric)
            msg += l_msg

        # decide on what the best classifier is based on the metric
        classifiers['best'] = self.decide_best_classifier(classifiers)

        msg += f"Classifiers: {json.dumps(classifiers, indent=4, cls=SafeEncoder)}" + "\n"
        msg += f"Artifacts: {json.dumps(artifacts, indent=4, cls=SafeEncoder)}" + "\n"

        logger.debug(f"Completed training",
                     extra=self.config.get_extra({
                         'transform': self.name,
                         'data': msg
                     }))

        return classifiers, artifacts


    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug("Start execution",
                     extra=self.config.get_extra({
                         'transform': self.name
                     }))
        self.state = state

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "policyapp.classifier")
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

            ###
            # first, some checks on the spec
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

            for f in ["name", "sources", "train", "predict"]:
                if f not in spec:
                    logger.exception(
                        f"Spec has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue

            ###
            # get all the data sources
            ##############
            # Re-write to use standard load_dataset(...) method
            # when using API-based spec and s3 data sources
            data = self.load_sources(spec)
            ##############
            if len(data) == 0:
                logger.exception("No datasources found, failing",
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                raise Exception("No datasources")

            ###
            # model training stage
            classifiers, artifacts = self.train_models(spec, data)

            ###
            # make predictions for each evaluation dataset
            # and store results
            results = self.make_predictions(spec, data, classifiers, artifacts)

            # Store the metadata with results
            self.store_metadata(spec, results)

        # Done
        logger.debug("Complete execution",
                     extra=self.config.get_extra({
                         'transform': self.name
                     }))

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
