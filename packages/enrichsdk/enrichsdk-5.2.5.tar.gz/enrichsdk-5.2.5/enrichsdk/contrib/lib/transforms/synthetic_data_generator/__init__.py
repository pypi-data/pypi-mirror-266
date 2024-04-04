import os
import json
import numpy as np
import pandas as pd
import time
import random
import sqlite3
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
import logging
import unidecode
from collections import defaultdict

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec

from faker import Faker

logger = logging.getLogger("app")


class SyntheticDataGeneratorBase(Compute):
    """
    Generate synthetic data given a specification

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of synthetic data in each column
            * instance: pre-defined faker-based instances
            * distribution: pre-defined from statistical distributions
            * custom: custom defined in base/derived class
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SyntheticDataGeneratorBase"
        self.description = "Generate synthetic data from a specification"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }
        self.fakeObj = None # for synthetic data generation, to be inited later on

    @classmethod
    def instantiable(cls):
        return False

    def init_faker_object(self):
        fakeObj = Faker()
        names           = defaultdict(fakeObj.name)
        addresses       = defaultdict(fakeObj.address)
        countries       = defaultdict(fakeObj.bank_country)
        phonenumbers    = defaultdict(fakeObj.msisdn)
        emaildomains    = defaultdict(fakeObj.domain_name)

        obj = {
            "faker": fakeObj,
            "generators": {
                "person-name": names,
                "country_2char": countries,
                "location-address": addresses,
                "phone_number": phonenumbers,
                "email_domain": emaildomains,
            }
        }

        return obj

    def get_handlers(self, spec):
        """
        Define various callbacks that take a dataframe, spec
        and compute.
        """
        return {}

    def get_spec_datasets(self, profile):
        if (not isinstance(profile, dict)) or ("datasets" not in profile):
            raise Exception("datasets not defined in profile")
        return profile["datasets"]

    ###########################################
    # Synthetic Data Generation
    ###########################################
    def generate_dataset(self, dataset):
        msg = ""

        # check dataset spec
        if (not isinstance(dataset, dict)):
            raise Exception("Dataset should be a valid dict")
        for p in ["columns"]:
            if (p not in dataset):
                err = f"Invalid dataset: {p} missing"
                raise Exception(err)

        name        = dataset["name"]
        columns     = dataset["columns"]
        store       = dataset.get("store", "store_default")
        nrecords    = dataset.get("nrecords", 100)

        msg += f"Generating dataset: {name}" + "\n"
        if dataset.get("nrecords") is None:
            msg += f"Number of records not specified, using default" + "\n"
        msg += f"Generating {nrecords} records" + "\n"

        # init an empty dict for the new dataset
        _d = {}

        # for each column that we need to generate
        for column in columns:
            for f in ["name", "generator", "method"]:
                if f not in column:
                    err = f"Invalid dataset-->column: {column}-->{f} missing"
                    raise Exception(err)

            msg += f"Generating column: {column['name']}" + "\n"

            success, _data, l_msg = self.generate_single_column(column, nrecords)
            msg += l_msg

            # no luck with data generation, move on
            if not success:
                continue

            # we have the synthetic data, collect it
            _d[column['name']] = _data


        # combine all generated columns into a single DF
        data = pd.DataFrame.from_dict(_d, orient='index').transpose()

        msg += note(data, f"Synthetic dataset: {name}") + "\n"

        logger.debug(
            f"Generated dataset: {name}",
            extra={"transform": self.name, "data": msg}
        )

        return data

    def generate_single_column(self, column, nrecords):
        success = False

        name        = column['name']
        generator   = column['generator']

        if generator == "faker":
            method = column['method']
            method_handler = None

            fakeObj = self.fakeObj['faker']

            if hasattr(fakeObj, method):
                method_handler = getattr(fakeObj, method)

            if not callable(method_handler):
                msg = f"Column: <{name}> -- Generator <{generator}> has no callable method <{method}>, skipping generation of column" + "\n"
                return success, None, msg

            # we have a callable handler
            data = []
            for _ in range(nrecords):
                data.append(method_handler())
            success = True

        elif generator == "distribution":
            msg = f"Column: <{name}> -- Distribution method not supported yet, skipping generation of column" + "\n"
            return success, None, msg

        elif generator == "custom":
            msg = f"Column: <{name}> -- Custom method not supported yet, skipping generation of column" + "\n"
            return success, None, msg


        msg = f"Generated {len(data)} records for column: {name}" + "\n"

        return success, data, msg


    ###########################################
    # Data Anonymization
    ###########################################
    def anonymize_dataset(self, spec, data):
        '''
        Anonymize a dataset given a spec
        '''
        msg = ""
        name    = spec['name']
        config  = spec['config']

        # whether to anonymize all columns or a spec is defined
        columns_to_anon = "all" if "columns" not in config else "given"

        df_columns = data.columns
        columns = config.get('columns', {})

        # run through each column and try to anonymize
        anon_columns = []
        for col_name, col_obj in columns.items():
            include = col_obj.get("include", "yes")
            if include != "yes":
                continue
            params = {}
            if col_name not in df_columns:
                msg += f"Column: {col_name} not found, skipping" + "\n"
            else:
                data[col_name], l_msg = self.anonymize_single_column(col_name, col_obj, data, params)
                anon_columns.append(col_name)
                msg += l_msg

        # drop the other columns is required by spec
        action = config.get("nontransformed", "retain")
        if action == "drop":
            data = data[anon_columns]

        msg += note(data, "Anonymized dataset") + "\n"

        logger.debug(
            f"Spec: {name} dataset anonymized",
            extra={"transform": self.name, "data": msg}
        )

        return data

    def anonymize_single_column(self, col_name, col_obj, data, params):
        '''
        Takes a dataset and anonymizes the specified column
        '''
        msg = ""

        # get the faker object
        fakeObj = self.fakeObj

        # setup handlers for the various anonymization types
        generators = {}
        # first for the lookup generators
        for g, lookup in fakeObj['generators'].items():
            generators[g] = {
                "type": "lookup",
                "handler": lookup
            }
        # then for the custom generators
        generators["numeric"] = {
            "type": "custom",
            "handler": "anon_numeric"
        }
        generators["email"] = {
            "type": "custom",
            "handler": "anon_email"
        }

        anon_type = col_obj['anon_type']
        _d = []
        if anon_type in generators:
            gen_type = generators[anon_type]['type']
            gen_handler = generators[anon_type]['handler']
            if gen_type == "lookup":
                # we call the apply only on the specific column
                data = data[col_name].apply(lambda x: gen_handler[x])
            else:
                handler = getattr(self, gen_handler)
                # we call the apply to the full dataframe, we may need other columns
                # return is only the relevant column
                data = handler(data, col_name, col_obj)
            msg += f"Column: {col_name} anonymized" + "\n"
        else:
            data = np.nan
            msg += f"Column: {col_name} -- No <{anon_type}> generator found, defaulting to NaN" + "\n"

        return data, msg

    #######################################
    # Custom generators go here
    #######################################
    def anon_numeric(self, data, col_name, column):
        '''
        Method to fuzz numeric data. Various fuzzing methods
        can be defined here.
        Input is the full dataframe, output is the relavant column being fuzzed.
        '''
        msg = ""

        method      = column.get("method", "perturb")
        params      = column.get("params", {})

        val = data[col_name]

        if method == "perturb":
            range = params.get("range", 0.05)
            val += random.uniform(-range*val, range*val)
        else:
            msg = f"Column {column['name']} -- Unknown method to anon column, setting default NaNs" + "\n"
            val = np.nan

        return val

    def anon_email(self, data, col_name, column):
        '''
        Method to anonymize email data. Can generate emails to match or not match
        data in some name field. Also respects original email domain distribution if required.
        Input is the full dataframe, output is the relavant column being anonymized.
        '''
        msg = ""

        match_names = column.get("match_names", True)
        if match_names is True:
            if "name_field" not in column:
                msg += f"Column {col_name} -- Unknown name field to match emails, setting random emails" + "\n"
                match_names = False
                return np.nan
            else:
                if column["name_field"] not in data.columns:
                    msg += f"Column {column['name']} -- name field not in dataframe, setting random emails" + "\n"
                    match_names = False
                    return np.nan

        def generate_email(fakeObj, row, col_name, column, match_names):
            # whitelist of email domains
            # if the origninal email is in this list, don't replace it
            # useful to maintain data distribution
            domain_whitelist = ['gmail.com',
                                'yahoo.com',
                                'hotmail.com',
                                'aol.com']

            email_col_name  = col_name
            orig_domain     = row[email_col_name].split('@')[1]

            # set the email domain first
            if column.get("dist", "yes") == "yes":
                # we need to ensure that the distribution of generated email domains
                # match what was present in the input
                # popular free email domains will carry over, while others will be
                # replaced with random domains while still retaining distribution
                if any([d==orig_domain for d in domain_whitelist]):
                    # retain the origninal domain name
                    domain = orig_domain
                else:
                    # get a new domain name
                    domain = fakeObj['generators']['email_domain'][orig_domain]
            else:
                # no need to match distribution of generated email domains
                domain = fakeObj['faker'].ascii_email().split('@')[1]

            if match_names is True:
                # we want to match the anon email with the name field
                name = row[column['name_field']]
                names = unidecode.unidecode(name).lower().split(' ')
            else:
                # we don't care about matching the anon email with the name field
                names = fakeObj['faker'].name().split(' ')

            firstname = names[0]
            lastname = names[-1]

            # possible variations of email
            nameparts = {
                1: f"{firstname}",
                2: f"{lastname}",
                3: f"{firstname}.{lastname}",
                4: f"{firstname}.{firstname[0]}.{lastname}",
                5: f"{firstname}.{lastname[0]}.{lastname}",
                6: f"{firstname}.{firstname[0]}.{lastname[0]}",
                7: f"{firstname}.{random.randint(1,10000)}",
                8: f"{firstname}_{random.randint(1,10000)}",
                9: f"{firstname}.{lastname}.{random.randint(1,10000)}",
            }
            choice = random.randint(1, len(nameparts))
            namepart = nameparts[choice]
            email = f"{namepart}@{domain}"

            return email

        val = data.apply(lambda x: generate_email(self.fakeObj, x, col_name, column, match_names), axis=1)

        return val




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

    def read_s3_data(self, filename, params, **kwargs):
        # assume we have a resolved s3fs object
        s3 = self.args['s3']
        if s3.exists(filename):
            df = pd.read_csv(s3.open(filename), **params)
            return df
        return None

    def get_dataset_s3(self, spec):
        """
        Use the dataset object to read the dataset
        """
        run_date    = self.args['run_date']
        name        = spec["name"]
        config      = spec['config']


        for f in ["dataset", "filename"]:
            if f not in config:
                msg = f"{f} param needed in config " + "\n"
                logger.exception(
                    f"Dataset: {name} -- skipping", extra={"transform": self.name, "data": msg}
                )
                return None

        source      = config.get('source', 'registry')
        dataset     = config['dataset']

        dataset     = config["dataset"]
        pieces      = dataset.split('-')
        dataset_main = "-".join(pieces[:-1])
        dataset_subset = pieces[-1]
        filename    = config["filename"]
        params      = config.get("params", {})

        cache = self.args.get("cache", False)
        cachename = f"{dataset}-{run_date}"
        cachefile = f"cache/{self.name}-anonymizer-cache-" + cachename + ".csv"

        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                msg = f"Location: {cachefile}" + "\n"
                df = pd.read_csv(cachefile, **params)
                msg += note(df, f"Cached {dataset}") + "\n"
                logger.debug(f"Read cached {name}", extra={"transform": self.name, "data": msg})
                return df

        if source == "registry":
            if not hasattr(self, "get_dataset"):
                raise Exception(
                    "get_dataset_s3 expects get_dataset method"
                )
            datasetobj = self.get_dataset(dataset_main) # this method should be defined in the derived class

            if hasattr(self, 'update_doodle'):
                self.update_doodle(datasetobj, filename)

            df, metadata = datasetobj.read_data(
                run_date,
                run_date,
                filename=filename,
                readfunc=self.read_s3_data,
                params=params,
            )
        elif source == "direct":
            params = {}
            df = self.read_s3_data(filename, params)
            metadata = { "files": [filename] }
        else:
            logger.exception(
                f"Dataset: {name} -- unknown source param: {source}, skipping", extra={"transform": self.name}
            )
            return None

        msg = note(df, f"Fresh {dataset}") + "\n"
        logger.debug(f"Read fresh {name}", extra={"transform": self.name, "data": msg})

        # Cache it for future use...
        if cache:
            df.to_csv(cachefile, index=False)

        # Insert lineage if possible
        lineage = None
        if ("files" in metadata) and (len(metadata["files"]) > 0):
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": [metadata["files"][-1]],
                    },
                ],
            }

        if not self.state.has_frame(spec['name']):
            self.update_frame(spec, f"Dataset: {dataset}", df, lineage)

        return df


    def load_dataset(self, spec, datasets):

        name        = spec['name']
        generate    = spec.get('generate')
        config      = spec['config']
        dataset     = config['dataset']

        # first, get the dataset nature
        nature = None
        paths = datasets[dataset].paths
        for path in paths:
            if path['name'] == 'default':
                nature = path['nature']
                break

        try:
            if nature == "db":
                data = self.read_db_source(spec)
            elif nature == "s3":
                data = self.get_dataset_s3(spec)
            elif (
                (generate is not None)
                and (generate in handlers)
                and (callable(handlers[generate]))
            ):
                data = handlers[generate](spec)
            elif (generate is not None) and (hasattr(self, generate)):
                data = getattr(self, generate)(spec)
            else:
                raise Exception(f"Dataset: {name} -- Invalid specification")
        except:
            msg =  "Could not load data, either nature or handlers not valid" + "\n"
            logger.exception(
                f"Dataset: {name} -- Generation failed", extra={"transform": self.name, "data": msg}
            )
            raise

        return data

    def s3_store_result(self, dataset, data):

        name        = dataset['name']
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()

        # get the dataframe and
        # add additional columns
        df = data
        df["__run_date__"] = run_date

        # where are we storing it?
        file   = os.path.join(self.args['s3root'], f"{run_date}/{name}.csv")

        # write to s3
        with s3.open(file, 'w') as fd:
            df.to_csv(fd, index=False)

        msg = f"s3 location: {file}" + "\n"

        logger.debug(f"Wrote dataset: {name} to S3",
                        extra={"transform": self.name,
                                "data": msg})

    def store_result(self, dataset, data):
        name    = dataset['name']
        store   = dataset.get("store", "s3")

        if store == "s3":
            # Now store in s3
            self.s3_store_result(dataset, data)
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

        # Send a message to SQL export that it should export
        self.state.msgpush(from_transform=self.name,
                           to_transform="SQLExport",
                           data={
                               'name': 'syndata',
                               'frames': [dataset['name']]
                           })

        #################################
        # also write to SQLLite
        # remove this when we figure out
        # how to do it from the pipeline
        # problem is -- output dataframe names can be dynamic, based on spec
        #   run_date    = self.args['run_date']
        #   s3          = self.args['s3']
        #   r_sqlfile   = os.path.join(self.args['s3root'], f"{run_date}/syndata.sqlite")
        #   l_sqlfile   = os.path.join(self.args['s3root'], f"syndata.sqlite.latest")
        #   cachefile   = f"cache/syndata.sqlite"

        #   conn = sqlite3.connect(cachefile)
        #   data.to_sql(name, conn, if_exists='replace', index=False)

        #   s3.put(cachefile, r_sqlfile)
        #   s3.put(cachefile, l_sqlfile)

        #   logger.debug("Storing as SQLite",
        #                extra={
        #                    'transform': self.name,
        #                    'data': f"Location(s): {r_sqlfile}, {l_sqlfile}" + "\n"
        #                })

        #################################

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # init the faker object for data generation
        self.fakeObj = self.init_faker_object()

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "syntheticdata")
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

        # get the dataset lookup table
        customer_datasets = profilespec.construct_dataset_list(self, profile)

        # Now go through each dataset and generate synthetic data for it
        for spec in specs:

            process_spec = True

            enabled = spec.get("enable", True)
            if not enabled:
                logger.debug(
                    f"Spec <{spec.get('name', 'NO NAME')}> not enabled, skipping.",
                    extra={"transform": self.name}
                )
                process_spec = False
                continue

            for f in ["name", "config"]:
                if f not in spec:
                    logger.error(
                        f"Spec has no {f} param set, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    process_spec = False
                    break

            if process_spec == False:
                # something is wrong with this spec, skip it
                continue

            # process the spec
            name    = spec['name']
            action  = spec.get('action', 'anonymize')

            if action == 'generate':
                # we have a generate a synthetic dataset
                frametype = "synthetic"
                data = self.generate_dataset(spec)
            elif action == 'anonymize':
                # we have to anonymize a given dataset
                frametype = "anonymized"
                # frist, load it
                data = self.load_dataset(spec, customer_datasets)

                # then, anonymize it
                if data is not None:
                    data = self.anonymize_dataset(spec, data)
                else:
                    msg = "Could not anonymize dataset" + "\n"
                    logger.exception(
                        f"Spec: {spec['name']} -- skipping",
                        extra={"transform": self.name}
                    )
            else:
                logger.exception(
                    f"Unknown action param in spec, skipping spec: {spec['name']}",
                    extra={"transform": self.name}
                )

            # store the generated dataset
            if data is not None:
                self.store_result(spec, data)

                # update frame for pipline
                description = spec.get(f"desc -- {frametype}", f"{frametype.title()} generated dataset")
                lineage = {
                    "type": "lineage",
                    "transform": self.name,
                    "dependencies": [
                        {
                            "type": "file",
                            "nature": "input",
                            "objects": [spec.get("filename", "__NEW__")],
                        },
                    ],
                }
                self.update_frame(
                    spec,
                    description,
                    data,
                    lineage,
                )

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
