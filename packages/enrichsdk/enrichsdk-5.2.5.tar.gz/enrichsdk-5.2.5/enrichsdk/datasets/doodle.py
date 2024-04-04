import os
import logging
import json
import traceback
import requests
import numpy as np
from datetime import datetime, timedelta

from enrichsdk.lib import get_credentials_by_name
from enrichsdk.utils import SafeEncoder, make_safely_encodable
from enrichsdk.datasets.generators import handlers as shared_generators

logger = logging.getLogger('app')

class Doodle(object):

    def __init__(self, cred, *args, **kwargs):
        """
        default
        """
        self.cred = cred
        self.generators = kwargs.pop('generators', {})
        self.purpose = None
        super().__init__(*args, **kwargs)

    def get_url(self):
        """
        Get base url
        """
        cred = self.cred
        if isinstance(cred, str):
            server = cred
        elif isinstance(cred, dict) and ('url' in cred):
            server = cred['url']
        elif isinstance(cred, dict) and ('uri' in cred):
            server = cred['uri']
        else:
            raise Exception("Unable to compute the url")

        server += "/docs"
        return server

    def access_server(self, path, params={}, data={}, method='get'):
        """
        Get/Post from doodle server
        """

        cred = self.cred
        if isinstance(cred, str):
            server = cred
        elif isinstance(cred, dict) and ('url' in cred):
            server = cred['url']
        elif isinstance(cred, dict) and ('uri' in cred):
            server = cred['uri']
        else:
            raise Exception("Invalid server details")

        if server.endswith("/"):
            server = server[:-1]

        if path.startswith("/"):
            path = path[1:]

        headers = {
            'Accept': 'application/json'
        }

        # Try all possible keys
        for k in ['key', 'api_key', 'apikey']:
            if k in cred:
                headers['X-API-Key'] = cred[k]
                break

        extra= { "verify": False }
        if 'basicauth' in cred:
            auth = (cred['basicauth']['username'], cred['basicauth']['password'])
            extra['auth'] = auth

        url = f"{server}/{path}"

        try:
            if method == 'post':
                response = requests.post(url, params=params, headers=headers, json=data, **extra)
            elif method == 'patch':
                response = requests.patch(url, params=params, headers=headers, json=data, **extra)
            elif method == 'get':
                response = requests.get(url, params=params, headers=headers, **extra)
            else:
                raise Exception(f"Unknown method: {method}")
        except Exception as e:
            logger.exception("Unable to access server")
            return 500, str(e)

        try:
            result = response.json()
        except:
            result = {
                'error': response.content.decode('utf-8')
            }


        return response.status_code, result


    def list_catalogs(self,
                      only_active=True,
                      offset: int = 0,
                      limit: int = 10,
                      order_by: str = None):
        """
        Search the catalogs
        """

        params = {
            'only_active': only_active,
            'offset': offset,
            'limit': limit,
            'order_by': order_by
        }

        status, result = self.access_server("/api/v1/catalogs",
                                            params=params)
        if status >= 300:
            raise Exception(f"Could not list catalogs")

        return result

    def get_catalog(self, catalog_id):
        """
        Get the details of one catalog
        """
        status, result = self.access_server(f"/api/v1/catalogs/{catalog_id}")

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)
        return result

    def search_catalogs(self,
                      only_active=True,
                      name: str = None,
                      version: str = None,
                      offset: int = 0,
                      limit: int = 10,
                      query: str = None,
                      modified_since: datetime = None,
                      modified_before: datetime = None,
                      order_by: str = None):
        """
        Search the catalogs
        """

        params = {
            'only_active': only_active,
            'name': name,
            'version': version,
            'offset': offset,
            'limit': limit,
            'query': query,
            'modified_since': modified_since,
            'modified_before': modified_before,
            'order_by': order_by
        }

        status, result = self.access_server(f"/api/v1/catalogs/search",
                                            params=params)

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result

    def find_catalog(self, name, version):
        """
        Find one catalog with a precise name and version
        """

        result = self.search_catalogs(name=name,
                                      version=version)

        if len(result) > 1:
            raise Exception(f"Multiple {len(result)} catalogs. Expecting one")

        if len(result) == 0:
            raise Exception(f"No catalog found {name}:{version}")

        return result[0]

    ##################################################
    # Lookup and update sources
    ##################################################
    def list_sources(self,
                     catalog_id=None,
                     only_active=True,
                     offset: int = 0,
                     limit: int = 1000,
                     order_by: str = None):
        """
        List available sources for a catalog
        """

        params = {
            'catalog_id': catalog_id,
            'only_active': only_active,
            'offset': offset,
            'limit': limit,
            'order_by': order_by
        }

        status, result = self.access_server("/api/v1/sources",
                                            params=params)

        if status >= 300:
            logger.error("Failed to list sources",
                         extra={
                             'data': str(result)
                         })
            raise Exception(f"Could not find sources for catalog {catalog_id}")

        return result

    def get_source(self, source_id):
        """
        Update the feature with latest dataset information
        """
        status, result = self.access_server(f"/api/v1/sources/{source_id}")

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)
        return result

    def search_sources(self,
                       only_active=True,
                       name: str = None,
                       version: str = None,
                       catalog_id: str = None,
                       offset: int = 0,
                       limit: int = 10,
                       query: str = None,
                       modified_since: datetime = None,
                       modified_before: datetime = None,
                       order_by: str = None):
        """
        Search the sources
        """

        params = {
            'only_active': only_active,
            'name': name,
            'version': version,
            'catalog_id': catalog_id,
            'offset': offset,
            'limit': limit,
            'query': query,
            'modified_since': modified_since,
            'modified_before': modified_before,
            'order_by': order_by
        }

        status, result = self.access_server(f"/api/v1/sources/search",
                                            params=params)

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result


    def update_source(self, source_id, details):
        """
        Update the catalog with latest dataset information
        """

        status, result = self.access_server(f"/api/v1/sources/{source_id}",
                                            data=details,
                                            method="post")

        if status >= 300:
            logger.error("Failed to update source",
                         extra={
                             'data': str(result)
                         })
            raise Exception(f"Could not update source {source_id}")

        return result

    def add_source(self, catalog_id, details):
        """
        Update the catalog with latest dataset information
        """

        details['catalog_id'] = catalog_id
        status, result = self.access_server("/api/v1/sources",
                                            data=details,
                                            method="post")

        if status >= 300:
            logger.error("Failed to update source",
                         extra={
                             'data': str(result)
                         })
            raise Exception(f"Could not add source to {catalog_id}")

        return result

    ##################################################
    # Lookup and update features
    ##################################################
    def list_features(self,
                      source_id=None,
                      catalog_id=None,
                      only_active=True,
                      offset: int = 0,
                      limit: int = 5000,
                      order_by: str = None):

        """
        List available features for a source
        """


        params = {
            'source_id': source_id,
            'catalog_id': catalog_id,
            'only_active': only_active,
            'offset': offset,
            'limit': limit,
            'order_by': order_by
        }
        status, result = self.access_server("/api/v1/features",
                                            params=params)

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result

    def get_feature(self, feature_id):
        """
        Update the feature with latest dataset information
        """
        status, result = self.access_server(f"/api/v1/features/{feature_id}")


        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result

    def search_features(self,
                        only_active=True,
                        name: str = None,
                        version: str = None,
                        catalog_id: str = None,
                        source_id: str = None,
                        offset: int = 0,
                        limit: int = 10,
                        query: str = None,
                        modified_since: datetime = None,
                        modified_before: datetime = None,
                        order_by: str = None):
        """
        Search the features
        """

        params = {
            'only_active': only_active,
            'name': name,
            'version': version,
            'catalog_id': catalog_id,
            'source_id': source_id,
            'offset': offset,
            'limit': limit,
            'query': query,
            'modified_since': modified_since,
            'modified_before': modified_before,
            'order_by': order_by
        }

        status, result = self.access_server(f"/api/v1/features/search",
                                            params=params)

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result

    def update_feature(self, feature_id, details):
        """
        Update the feature with latest dataset information
        """
        status, result = self.access_server(f"/api/v1/features/{feature_id}",
                                            data=details,
                                            method="post")

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)
        return result

    def add_feature(self, catalog_id, source_id, details):
        """
        Update the source with latest feature information
        """

        details['catalog_id'] = catalog_id
        details['source_id'] = source_id

        status, result = self.access_server("/api/v1/features",
                                            data=details,
                                            method="post")

        if status >= 300:
            error = json.dumps(result['detail'])
            raise Exception(error)

        return result

    ####################################################
    # Performance
    ####################################################
    def get_performance(self, pid):
        status, result = self.access_server("/api/v1/performance",
                                            params={
                                                'pid': str(pid)
                                            })
        if status >= 300:
            raise Exception(f"Could not obtain performance data")

        return result

    ####################################################
    # Read source
    ####################################################
    def compute_source_paths(self, source, start, end):
        """
        Read the source data from start to end dates...
        """

        """
        Sample matching specification
        {
            "generate": "generate_datetime_daily",
            "compare": "compare_datetime_pattern_match_range",
            "pattern": "%Y-%m-%d",
            "filename": "data.csv",
            "searchpaths": [
                "enrich-terrapay/backup/tip.terrapay.com/rawdata/queries/txn_value"
            ],
            "matchingpath": "enrich-terrapay/backup/tip.terrapay.com/rawdata/queries/txn_value/2022-11-07/data.csv"
        }
        """

        try:
            match = source['details']['match']
        except:
            raise Exception("Match section is missing")

        generator = match.get('generate', None)
        if generator is None:
            raise Exception("No generator specified")
        elif ((generator not in self.generators) and
              (generator not in shared_generators)):
            raise Exception(f"Unknown generator: {generator}")

        # Special case of a fixed path
        if generator == 'static_path':
            if 'matchingpath' in match:
                return [match['matchingpath']]
            else:
                raise Exception("matchingpath is missing")


        # Rest of the cases
        generator = self.generators.get(generator, shared_generators.get(generator))

        # Get all the subdirs
        subdirs = generator(match, start, end)
        root = match['searchpaths'][0]
        filename = match['filename']

        paths = []
        for subdir in subdirs:
            paths.append(os.path.join(root, subdir['name'], filename))

        return paths

    def get_source_paths(self,
                         start, end,
                         name=None,
                         version="v1",
                         source_id=None):
        """
        Find all the source paths
        """
        if ((name is None) and (source_id is None)):
            raise Exception("name or source_id must be specified")

        if name is not None:
            sources = self.search_sources(name=name, version=version)
            if len(sources) > 0:
                source = sources[0]
            else:
                source = self.get_source(source_id)
        else:
            source = self.get_source(source_id)

        if not source['active']:
            logger.error("Inactive source: {source['id']}")

        paths = self.compute_source_paths(source, start, end)

        return source, paths


class TransformDoodle(Doodle):
    """
    Extension to Doodle to allow passing of transform
    information to the doodle server
    """

    def __init__(self, transform, state, *args, **kwargs):
        """
        """
        self.transform = transform
        self.state = state
        self.action = kwargs.pop('action', 'read')

        super().__init__(*args, **kwargs)


    def insert_access_metadata(self, details):
        """
        """
        metadata = self.transform.get_default_metadata(self.state)
        pipeline = metadata['pipeline']

        data = {
            "name": pipeline['name'],
            "usecase": pipeline['usecase'],
            "nature": "pipeline",
            "action": self.action
        }
        key = "%(usecase)s:%(name)s:%(nature)s:%(action)s" % data

        if 'metadata' not in details:
            details['metadata'] = {}
        if 'access' not in details['metadata']:
            details['metadata']['access'] = {}
        details['metadata']['access'][key] = data

    def add_source(self, catalog_id, details):
        """
        Insert access metadata before posting
        """
        self.insert_access_metadata(details)
        return super().add_source(catalog_id, details)

    def update_source(self, source_id, details):
        """
        Insert access metadata before posting
        """
        self.insert_access_metadata(details)
        return super().update_source(source_id, details)

if __name__ == "__main__":

    cred = get_credentials_by_name('doodle')

    doodle = Doodle(cred)

    sources = doodle.list_sources()
    for source in sources:
        print("Processing", source['name'])
        try:
            source, paths = doodle.get_source_paths(start=datetime.today() + timedelta(days=-7),
                                                    end=datetime.today(),
                                                    name=source['name'],
                                                    version=source['version'])

            print(json.dumps(paths, indent=4))
        except Exception as e:
            print("Error!", e)
