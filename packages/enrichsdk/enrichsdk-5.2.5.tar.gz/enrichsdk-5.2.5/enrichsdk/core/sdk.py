import os
import sys
import json
import yaml
import copy
import re
import traceback
import logging
from jinja2 import Template

from os.path import exists, join
import pandas as pd

# Connectors...
import pymongo
from sqlalchemy import create_engine

from ..lib.exceptions import *
from .node import *
from .mixins import *

logger = logging.getLogger("app")

__all__ = [
    "Source",
    "Sink",
    "Trigger",
    "Compute",
    "TransformSpec",
    "NotificationIntegration",
    "DatabaseIntegration",
]

##################################################
# Transform objects
##################################################
class Source(Transform):
    """
    This is a special transform that introduces dataframes into the
    state.

    This transform typically extracts information from thirdparty
    tools and services such as APIs, databases.
    """

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.roles_supported = ["Source"]
        self.roles_current = "Source"

    def sample_inputs(self):
        return []

    def is_source(self):
        return True


class Sink(Transform):
    """
    This is a special transform that dumps dataframes that are in the
    state to some thirdparty service such as file system, database,
    cloud storage etc.
    """

    def __init__(self, *args, **kwargs):
        super(Sink, self).__init__(*args, **kwargs)
        self.roles_supported = ["Sink"]
        self.roles_current = "Sink"

    def is_sink(self):
        return True


class Compute(Transform):
    """

    This is a typical transform that wrangles data. It could introduce
    new frames and transform existing frames.

    This will mainly be pandas code but may also be spark/other
    code. The framework itself is agnostic to what the transform
    does.

    """

    def __init__(self, *args, **kwargs):
        super(Compute, self).__init__(*args, **kwargs)
        self.roles_supported = ["Compute"]
        self.roles_current = "Compute"

class TransformSpec(Transform):
    """
    Transform that supports a specification-based configuration. This
    transform requires spec.json file to be available in the transform
    directory.  The main value of this subclass is to eliminate the
    boiler plate that is required for every transform.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the transform specification
        self.transform_spec = self.load_tspec()

        # Load the queries...
        self.transform_input_queries = {}

        # Actions
        self.validate_tspec()
        self.load_input_queries()

        # Store the name and description
        for col in ['name', 'description']:
            setattr(self, col, self.transform_spec.get(col, "Unknown"))

        logger.debug("Loaded specification",
                     extra={
                         'transform': self.name,
                         'data': json.dumps(self.transform_spec, indent=4)
                     })

    def validate_tspec(self):
        """
        Validate specification
        """
        tspec = self.transform_spec
        if tspec is None:
            raise Exception("Could not find transform specification")

        if not isinstance(tspec, dict) or len(tspec) == 0:
            raise Exception("Transform specification is either not a dictionary or is empty ")

        if "spec" not in tspec:
            raise Exception("Transform specification required 'spec' element")
        if not isinstance(tspec['spec'], dict) or len(tspec['spec']) == 0:
            raise Exception("Transform specification's 'spec' element should a valid non-empty dict")

        spec = tspec['spec']
        for section in ['credentials', 'input_datasets', 'output_datasets',  'queries']:
            if section in spec:
                if not isinstance(spec[section], list):
                    raise Exception(f"Specification section {section} should be a list of dicts")
                for entry in spec[section]:
                    if not isinstance(entry, dict) or len(entry) == 0:
                        raise Exception(f"Specification section {section} should be a list of non-trivial dicts")

        missing = []
        if 'input_queries' in spec:
            input_queries = spec['input_queries']
            for qspec in input_queries:
                for key  in ['name', 'database', 'filename', 'credential']:
                    if key not in qspec:
                        missing.append(f"[input_queries] {key}")

        if len(missing) > 0:
            logger.error("Missing configuration elements",
                         extra={
                             'transform': self.name,
                             'data': ", ".join(missing)
                         })
            raise Exception("Invalid configuration")

    def load_tspec(self):
        """
        Find and load transform specification

        This looks for spec.json and spec.yaml
        """
        subclspath = sys.modules[self.__module__].__file__
        subclsdir = os.path.dirname(subclspath)
        spec = None

        if exists(join(subclsdir, "spec.json")):
            spec = json.load(open(join(subclsdir, "spec.json")))
        elif  exists(join(subclsdir, "spec.yaml")):
            spec = yaml.safe_load(open(join(subclsdir, "spec.yaml")))
        elif  exists(join(subclsdir, "spec.yml")):
            spec = yaml.safe_load(open(join(subclsdir, "spec.yml")))

        if spec is None:
            raise Exception("Transform specification file (spec.json/spec.yaml) is required")

        return spec

    def load_input_queries(self):
        """
        Find and load input queries at the time of initialization.
        """

        subclspath = sys.modules[self.__module__].__file__
        subclsdir = os.path.dirname(subclspath)

        notfound = []
        queries = self.transform_spec['spec'].get('input_queries',[])
        for q in queries:
            """
            q = {
                "name": "edit_name",
                "description": "edit description",
                "credential": "tdb"
            }
            """
            name = q['name']
            filenames = [
                name,
                f"{name}.sql",
                f"{name}.mql",
            ]

            if "filename" in q:
                filenames.append(q['filename'])

            found = False
            for f in filenames:
                path = os.path.join(subclsdir, f)
                try:
                    if not os.path.exists(path):
                        continue
                    content = open(path).read()
                    if name in self.transform_input_queries:
                        logger.warning(f"Duplicate query: {name}")
                        continue
                    self.transform_input_queries[name] = {
                        'name': name,
                        "filename": f,
                        'template': content
                    }
                    found = True
                    break
                except:
                    logger.exception(f"Failed to read: {name}",
                                     extra={
                                         'transform': self.name
                                     })

            if not found:
                notfound.append(name)

        if len(notfound) > 0:
            logger.info("Input queries not loaded: {len(notfound)}",
                        extra={
                            'transform': self.name,
                            'data': ", ".join(notfound)
                        })

    def preload_clean_args(self, args):
        """
        Load the credentials from the transform specification
        """

        args = super().preload_clean_args(args)

        # Gather credentials
        if 'transform_credentials' in args:
            raise Exception("conflict in args: transform_credentials")
        args['transform_credentials'] = {}

        # Global credentials
        credentials = self.transform_spec.get('spec', {}).get('credentials', [])
        credentials = [c['name'] for c in credentials if ((isinstance(c, dict)) and ('name' in c))]

        # Load credentials specified in input or output queries
        for section in ['input_datasets', 'output_datasets',
                        'input_queries', 'output_queries']:
            for d in self.transform_spec.get('spec', {}).get(section, []):
                if (isinstance(d, dict ) and ('credential' in d)):
                    if d['credential'] not in credentials:
                        credentials.append(d['credential'])

        for name in credentials:
            if name in args['transform_credentials']:
                continue
            args['transform_credentials'][name] = self.get_credentials(name)

        return args


    def get_input_query_params(self, qspec):
        """
        Get the rendering parameters, if any, for the query template

        Args:
           qspec (dict): Specification of the query (filename etc.)

        Returns
           dict: Dictionary with parameters that is passed to the query template renderer

        """
        return {}

    def get_input_query_template(self, qspec):
        """
        Get the input query corresponding to a name
        """

        name = qspec['name']
        if name not in self.transform_input_queries:
            raise Exception(f"Query not found: {name}")

        return self.transform_input_queries[name]['template']

    def get_mongo_client(self, qspec):

        cred = qspec['credential']
        cred = self.args['transform_credentials'][cred]

        # Connect to server
        uri = cred['uri']
        client = pymongo.MongoClient(uri)

        return client

    def execute_mongo_query(self, qspec, query):

        name = qspec['name']

        try:

            # Get the client...
            client = self.get_mongo_client(qspec)

            # Get the database
            db = client[qspec['database']]

            # Now run the pymongo query..
            docs = eval(query)
            if not isinstance(docs, list):
                docs = list(docs)

            df = pd.DataFrame(docs)

        except:
            logger.exception(f"Error while running {name}")
            raise

        return df, {}

    def get_sql_engine(self, qspec):

        cred = qspec['credential']
        cred = self.args['transform_credentials'][cred]

        # Connect to server
        uri = cred['uri']

        # Create an engine
        engine = create_engine(uri)

        return engine

    def execute_sql_query(self, qspec, query):

        name = qspec['name']

        try:

            # Get the connection
            engine = self.get_sql_engine(qspec)

            # Run the query
            df = pd.read_sql(query, con=engine)

        except:
            logger.exception(f"Error while running {name}")
            raise

        return df, {}

    def execute_input_query(self, qspec, query):
        """
        Override this for non-SQL backends
        """

        cred = qspec['credential']
        cred = self.args['transform_credentials'][cred]

        dbtype = cred.get('dbtype', 'unknown')
        if dbtype == 'mongo':
            return self.execute_mongo_query(qspec, query)
        elif dbtype in ['postgres', 'mysql']:
            return self.execute_sql_query(qspec, query)

        # Now run the query...
        df = pd.DataFrame([{'a': 2}])

        return df, {}

    def read_input_query(self, qspec):
        """
        Run the named query rendered using the params
        and using the credential name
        """
        metadata = {}

        try:

            # First get the params...
            params = self.get_input_query_params(qspec)

            # Instantiate the query template
            query_template = self.get_input_query_template(qspec)

            template = Template(query_template)
            query = template.render(**params)

            df, metadata = self.execute_input_query(qspec, query)

        except:
            logger.exception(f"Unable to instantiate the query: {qspec['name']}")
            raise

        return df, {}

    def get_supported_extra_args(self):

        default_extra_args = super().get_supported_extra_args()

        # Now add some more...
        tspec = self.transform_spec
        more_args = tspec.get('spec', {}).get('args', [])

        # Now check if all the required elements exist in the test
        # data...
        tspec = self.transform_spec
        more_args = tspec.get('spec', {}).get('args', [])

        missing_args = {}

        conf = self.testdata.get("conf", {})
        args = conf.get('args', {})

        # Now check if we have all required
        for a in more_args:
            name = a['name']
            default = a['default']
            required = a['required']
            if ((required) and (name not in args)):
                missing_args[name] = default

        if len(missing_args) == 0:
            return default_extra_args + more_args

        msg = "Missing arguments: " + ", ".join(missing_args.keys())  + "\n"
        instance = list(missing_args.items())[0]
        msg += "These arguments can be specified as:\n"
        msg += """\n
def __init__(self, *args, **kwargs):
      super().__init__(*args, *kwargs)
      self.testdata = {
          "conf": {
              "args": {
                  "%s": "%s"
                  ....
              }
          }
      }
        """ % instance
        logger.error("Missing args in testdata",
                     extra={
                         'transform': self.name,
                         'data': msg
                     })
        raise Exception("Missing args in testdata")



class Trigger(Sink):
    """
    This transform is expected to run after the computation
    is over. This is a particular kind of sync

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NotificationIntegration(Integration):
    """
    Search interface dashboard

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.extend(["integration", "notification"])


class DatabaseIntegration(Integration):
    """
    Write to database

    .. deprecated:: 2.0

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.extend(["integration", "database"])
