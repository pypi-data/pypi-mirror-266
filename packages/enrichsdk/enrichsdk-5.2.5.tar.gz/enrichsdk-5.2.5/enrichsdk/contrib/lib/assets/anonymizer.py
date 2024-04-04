import os
import sys
import json
import random
import copy
import hashlib
import pickle
import logging
import traceback
from collections import defaultdict

import seaborn as sns
from faker import Faker
import pandas as pd
import numpy as np

from enrichsdk.utils import SafeEncoder, note
from enrichsdk.lib import get_credentials_by_name
from enrichsdk.contrib.lib.assets import LLMTextGenerator

__all__ = [
    'BaseAnonymizer',
    'CachingAnonymizer',
    'AnonymizerMixin'
]

logger = logging.getLogger('app')

class BaseAnonymizer(object):

    def __init__(self, textgen_cred, *args, **kwargs):
        """
        default
        """
        # set vars
        self.textgen_cred = textgen_cred

        # what are our possible column classes
        self.column_classes = {
            'person': 'person-name',
            'country': 'country_2char',
            'address': 'location-address',
            'phone': 'phone_number',
            'mobile': 'phone_number',
            'email': 'email',
            'identifier': 'categorical',
            'number': 'numeric',
            'latlong': 'numeric',   # need to write a custom anonymizer
            'datetime': 'numeric',  # need to write a custom anonymizer
            'location': 'categorical',
        }

        # init a Faker object
        self.fakeObj  = self.init_faker_object()

        super().__init__(*args, **kwargs)


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

    ###########################################
    # Column Classification
    ###########################################
    def classify_columns_naive(self, df, columns):
        for col_name, col_obj in columns.items():

            if pd.api.types.is_numeric_dtype(df[col_name]):
                anon_type = "numeric"
            elif pd.api.types.is_string_dtype(df[col_name]):
                anon_type = "categorical"
            elif pd.api.types.is_categorical_dtype(df[col_name]):
                anon_type = "categorical"
            else:
                anon_type = "categorical"

            columns[col_name]['anon_type'] = anon_type
            columns[col_name]['values'] = df[col_name].head().values.tolist()
            columns[col_name]['dtype'] =  df[col_name].dtypes.name

        return columns

    def classify_columns_common(self, df, columns, method="scribble_llm", spec={}):

        cache = spec.get('cache',{})

        # do the column classification
        if method == "scribble_llm":
            # init the credentials

            # first, do a naive classification so we can find the non-numeric columns
            cols = self.classify_columns_naive(df, columns)
            cols_to_classify = {}
            for c, o in list(cols.items()):
                if o['anon_type'] != 'numeric':
                    if c in cache:
                        cols[c]['anon_type'] = cache[c]
                    else:
                        cols_to_classify[c] = o

            # figure out what are the columns we need to classify
            class_str   = ",".join([c for c, o in self.column_classes.items()])
            class_len   = len(self.column_classes)

            if len(cols_to_classify) > 0:
                cols_str    = ",".join([c for c, o in cols_to_classify.items()])

                prompt = f"""Assume you have {class_len} classes:
{class_str}
How would you classify the following columns in a database table:
{cols_str}"""

                cred = get_credentials_by_name(self.textgen_cred)
                generator = LLMTextGenerator(cred)
                result = generator.generate_text(prompt=prompt)
                if result['success'] == True:
                    # get the class asignments
                    classes = result['text'].split('\n')
                    for c in classes:
                        if ":" not in c:
                            continue
                        [col_name, label] = c.split(":")
                        col_name = col_name.strip().lower()
                        label = label.strip().lower()
                        cache[col_name] = columns[col_name]['anon_type'] = self.column_classes[label]

            else:
                # something went wrong, so we have to fall back on the default classification method
                columns = self.classify_columns_naive(df, columns)

        else:
            # fall back on the default classification method
            columns = self.classify_columns_naive(df, columns)

        return columns


    ###########################################
    # Data Anonymization
    ###########################################
    def anonymize_dataset(self, df, spec={}):
        """
        Anonymize a dataset given a spec.
        The spec defines how the dataset should be handled
        and what kinds of anonymization needs to be performed.
        If no spec is given, we infer one from the dataset.
        """

        name    = spec.get('name', 'dataframe-anonymizer')
        config  = spec.get('config', {})
        columns = config.get('columns', {})
        sample  = config.get('sample', -1)

        # if no columns are specified
        # we need to anonymize all available columns
        if len(columns) == 0:
            _columns = {}
            for c in df.columns:
                _columns[c] = {"include": "yes"}
            columns = _columns

        # Sanity check...
        for c, details in columns.items():
            if not isinstance(details, dict):
                raise Exception(f"column specification {c} should be a dictionary")

        # Sample if required
        if ((sample > 0) and (sample < len(df))):
            df = df.sample(sample)

        # we need to classify the columns
        # so we know what kind of anonymization to use
        columns = self.classify_columns_common(df, columns, spec)

        # prepare for anonymization
        anon_cols       = []
        missing_cols    = []
        error_cols      = []
        anon_actions    = {}
        dropped_cols    = []
        retained_cols   = []
        anon_df         = df.copy()

        # run through each column and try to anonymize
        for col_name, col_obj in columns.items():
            include = col_obj.get("include", "yes")
            if include == "yes":
                if col_name not in df.columns:
                    # this column in the spec is missing in the DF, make note of it
                    missing_cols.append(col_name)
                else:
                    try:
                        # anonymize this single column
                        anon_df[col_name], msg = self.anonymize_single_column(col_name, col_obj, df)
                        # make note of the column name
                        anon_cols.append(col_name)
                        # make note of the anonymization action
                        anon_actions[col_name] = msg
                    except Exception as e:
                        traceback.print_exc()
                        error_cols.append(col_name)

        # drop the other columns if required by spec
        nontransformed = config.get("nontransformed", "retain")
        if nontransformed == "drop":
            dropped_cols = [c for c in df.columns if c not in anon_cols]
            anon_df = anon_df[anon_cols]
        else:
            retained_cols = [c for c in df.columns if c not in anon_cols]

        # construct the result object
        anon_data = {
            "df": anon_df,
            "actions": anon_actions,
            "anon_cols": anon_cols,
            "missing_cols": missing_cols,
            "error_cols": error_cols,
            'dropped_cols': dropped_cols,
            'retained_cols': retained_cols,
        }

        success = True if len(anon_cols)>0 else False

        return success, anon_data

    def anonymize_single_column(self, col_name, col_obj, df, params={}):
        """
        Takes a dataset and anonymizes the specified column
        """

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
        generators["categorical"] = {
            "type": "custom",
            "handler": "anon_categorical"
        }
        generators["email"] = {
            "type": "custom",
            "handler": "anon_email"
        }

        anon_type = col_obj.get('anon_type')

        _d = []
        if anon_type in generators:
            gen_type = generators[anon_type]['type']
            gen_handler = generators[anon_type]['handler']
            if gen_type == "lookup":
                # we call the apply only on the specific column
                data = df[col_name].apply(lambda x: gen_handler[x])
                l_msg = ""
            else:
                handler = getattr(self, gen_handler)
                # we call the apply to the full dataframe, we may need other columns
                # return is only the relevant column
                data, l_msg = handler(df, col_name, col_obj)
            msg = f"Anonymized using <{gen_handler}> handler of <{gen_type}> type." + l_msg
        else:
            data = np.nan
            msg = f"No <{anon_type}> generator found, defaulting to NaN."

        return data, msg


    #######################################
    # Custom anonymizers go here
    #######################################
    def anon_numeric(self, df, col_name, column):
        """
        Method to fuzz numeric data. Various fuzzing methods can be defined here.
        Input is the full dataframe, output is the relavant column being fuzzed.
        """
        msg = ""

        method      = column.get("method", "perturb")
        params      = column.get("params", {})

        val = df[col_name].fillna(0)

        if method == "perturb":
            range = params.get("range", 0.05)
            val += random.uniform(-range*val, range*val)
        else:
            msg = f"Unknown method to anon NUMERIC column, setting default NaNs."
            val = np.nan

        return val, msg

    def anon_categorical(self, df, col_name, column):
        """
        Method to anonymize categorical data. Various anonymization methods can be defined here.
        Input is the full dataframe, output is the relavant column being anonymized.
        """
        msg = ""

        def generate_hash(txt):
            if pd.isnull(txt):
                return np.nan

            if not isinstance(txt, str):
                txt = str(txt)

            hashed = hashlib.md5(txt.encode('utf-8')).hexdigest()
            hashed = hashed[:-10]
            return hashed

        method      = column.get("method", "hash")
        params      = column.get("params", {})

        if method == "hash":
            val = df.apply(lambda x: generate_hash(x[col_name]), axis=1)
        else:
            msg = f"Unknown method to anon CATEGORICAL column, setting default NaNs."
            val = np.nan

        return val, msg

    def anon_email(self, df, col_name, column):
        """
        Method to anonymize email data. Can generate emails to match or not match
        data in some name field. Also respects original email domain distribution if required.
        Input is the full dataframe, output is the relavant column being anonymized.
        """
        msg = ""

        match_names = column.get("match_names", True)
        if match_names is True:
            if "name_field" not in column:
                msg = f"Unknown name field to match emails, setting random emails."
                match_names = False
                return np.nan, msg
            else:
                if column["name_field"] not in data.columns:
                    msg = f"name field not in dataframe, setting random emails."
                    match_names = False
                    return np.nan, msg

        def generate_email(fakeObj, row, col_name, column, match_names):

            email     = row[email_col_name]
            if pd.isnull(email):
                return np.nan

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

        val = df.apply(lambda x: generate_email(self.fakeObj, x, col_name, column, match_names), axis=1)

        return val, msg


class CachingAnonymizer(BaseAnonymizer):
    """
    Cache results of the classification
    """

    def __init__(self, cachepath, *args, **kwargs):
        self.cachepath = cachepath
        if os.path.exists(cachepath):
            try:
                self.cache = pickle.load(open(cachepath, 'rb'))
            except:
                self.cache = {}
                logger.exception("Unable to load anonymizer cache",
                                 extra={
                                     'data': cachepath
                                 })

        else:
            self.cache = {}

        super().__init__(*args, **kwargs)

    def update_cache(self):
        with open(self.cachepath, 'wb') as fd:
            pickle.dump(self.cache,
                        fd,
                        protocol=pickle.HIGHEST_PROTOCOL)


    def anonymize_dataset(self, df, spec={}):
        """
        Filter out column that neednt be computed
        """

        spec['cache'] = self.cache

        # Run the
        success, anon_data = super().anonymize_dataset(df, spec)

        self.update_cache()

        return success, anon_data

class AnonymizerMixin(object):
    """
    Embed the core anonymization functions in transforms
    """

    def anonymize_init(self, anonargs):
        """
        Initialize the anonymizer
        """

        if not hasattr(self, 'state'):
            raise Exception("Missing state attribute in transform")

        #=> Initialize the anonymization args
        if (('cache' not in anonargs) or
            ('textgen_cred' not in anonargs)):
            logger.error("Missing cache or textgencred",
                         extra={
                             'transform': self.name,
                             'data': json.dumps(anonargs, indent=4)
                         })
            raise Exception("Missing cache or textgencred")

        self.anonymizer = CachingAnonymizer(cachepath=anonargs['cache'],
                                            textgen_cred=anonargs['textgen_cred'])


        if 'targets' not in anonargs:
            logger.error("Missing targets for anonymization",
                         extra={
                             'transform': self.name,
                             'data': json.dumps(anonargs, indent=4)
                         })
            raise Exception("Missing anonymization targets")

        # => Clean the targets and store them after including the spec
        defaultspec = anonargs.get('spec', {
            'config': {
                'sample': 1000,
                'nontransformed': 'drop'
            }
        })

        targets = anonargs['targets']
        cleaned_targets = []
        for t in targets:
            if isinstance(t, str):
                t = {
                    'name': t,
                }
            if 'name' not in t:
                logger.warning("Anonymization target skipped",
                               extra={
                                   'transform': self.name,
                                   'data': json.dumps(t)
                               })
                continue

            if 'spec' not in t:
                t['spec'] = copy.copy(defaultspec)

            cleaned_targets.append(t)

        anonargs['targets'] = cleaned_targets

        logger.debug("Anonymization targets",
                           extra={
                               'transform': self.name,
                               'data': json.dumps(anonargs)
                           })

        self.anonargs = anonargs
        self.anonymization_actions = []

    def anonymize_target(self, name, df=None):

        anon_name = f"{name}_anonymized"

        target = None
        for spec in self.anonargs['targets']:
            if spec.get("name", "unknown") == name:
                target = spec
                break

        if target is None:
            return

        # => If df is not specified, then lookup the state
        if df is None:

            if not self.state.has_frame(name):
                logger.error(f"Missing {name} in state",
                             extra={
                                 'transform': self.name,
                             })
                return

            # => Now get the state
            detail = self.state.get_frame(name)

            # => Extract the dataframe to be anonymized
            df = detail['df']

        if ((df is None) or (len(df) == 0)):
            raise Exception(f"Missing or empty {name}")

        # Anonymize
        success, anon_data = self.anonymizer.anonymize_dataset(df, spec)

        # => Dont update it again if it is already present
        if self.state.has_frame(anon_name):
            return anon_data['df']


        msg = ""

        for attr, detail in anon_data.items():
            if attr == "df":
                msg += note(anon_data['df'], f"Anonymized {name}")
            elif "cols" in attr:
                msg += f"{attr}: {','.join(detail)}\n"
            elif attr == "actions":
                for k,v in detail.items():
                    msg += f"Action: {k} => {v}\n"
        logger.debug(f"Anonymized {name}",
                     extra={
                         'transform': self.name,
                         'data': msg
                     })

        # Track the anonymization status
        for column, action in anon_data['actions'].items():
            self.anonymization_actions.append({
                'frame': name,
                'column': column,
                'action': 'anonymized',
                'detail': action
            })

        for attr, label in {
                "missing_cols": "missing",
                "error_cols": "error",
                "dropped_cols": "dropped",
                "retained_cols": "retained"
            }.items():

            cols = anon_data.get(attr, [])
            for col in cols:
                self.anonymization_actions.append({
                    'frame': name,
                    'column': column,
                    'action': label,
                    'detail': ""
                })

        #=> Register the anonymized dataframe with state...
        anon_df = anon_data['df']

        # => Gather the update parameters
        updated_detail = {
            'df': anon_data['df'],
            'description': f"{name} anonymized",
            'transform': self.name,
            'frametype': 'pandas',
            'params': self.get_column_params(anon_name, anon_df) + [
                {
                    "type": "lineage",
                    "dependencies": [
                        {
                            "type": "dataframe",
                            "nature": "input",
                            "objects": [name]
                        }
                    ]
                }
            ],
        }

        # Update the state.
        # Do the same thing for the second update dataframe
        self.state.update_frame(anon_name, updated_detail, create=True)

        # => Return the dataframe..
        return anon_data['df']

    def anonymize_all_targets(self):

        targets = self.anonargs['targets']

        if len(targets) == 0:
            logger.debug("No anonymization targets found",
                         extra=self.config.get_extra({
                             'transform': self.name
                         }))
            return

        for t in targets:
            self.anonymize_target(t['name'])

    def anonymize_finalize(self):

        allactions = self.anonymization_actions
        if len(allactions) == 0:
            logger.warning("No valid anonymization actions",
                           extra={
                               'transform': self.name
                           })
            return

        # => Gather the changes made
        action_name = "anonymization_status"
        actiondf = pd.DataFrame(allactions)
        frames = list(actiondf['frame'].unique())
        updated_detail = {
            'df': actiondf,
            'description': f"Anonymization status",
            'transform': self.name,
            'frametype': 'pandas',
            'params': self.get_column_params(action_name, actiondf) + [
                {
                    "type": "lineage",
                    "dependencies": [
                        {
                            "type": "dataframe",
                            "nature": "input",
                            "objects": frames
                        }
                    ]
                }
            ],
        }

        # Update the state.
        # Do the same thing for the second update dataframe
        self.state.update_frame(action_name, updated_detail, create=True)


if __name__ == "__main__":

    diamonddf = sns.load_dataset("diamonds")

    anonymizer  = BaseAnonymizer(textgen_cred="openai-api")
    success, anon_data  = anonymizer.anonymize_dataset(diamonddf)
    print (f"Success: {success}")
    print (json.dumps(anon_data, indent=4, cls=SafeEncoder))

    anonymizer  = CachingAnonymizer("anon.pickle",
                                  textgen_cred="openai-api")
    success, anon_data  = anonymizer.anonymize_dataset(diamonddf)
    print (f"Success: {success}")
    print (json.dumps(anon_data, indent=4, cls=SafeEncoder))

