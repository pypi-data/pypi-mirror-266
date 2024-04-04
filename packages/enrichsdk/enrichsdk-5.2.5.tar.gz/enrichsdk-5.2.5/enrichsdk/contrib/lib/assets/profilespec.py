import os
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json
import importlib.util
import sys

from enrichsdk.utils import SafeEncoder

###############################
# Profile handling
###############################
def get_profile(clsobj, spec_category):

    profile_source = clsobj.args.get('profile_source', 'file')
    if profile_source == "api":
        is_valid, profile, l_msg = get_profile_from_api(clsobj, spec_category)
    elif profile_source == "file":
        is_valid, profile, l_msg = get_profile_from_file(clsobj)
    else:
        raise Exception("profile_source={api/file} must be specified")

    msg = f"Profile source: {profile_source}" + "\n"
    msg += l_msg
    msg += f"Profile: {json.dumps(profile, indent=4, cls=SafeEncoder)}" + "\n"

    return is_valid, profile, msg

###############################
# API based profile
###############################
def call_api(apicred, urlsuffix):
    msg = ""
    apikey = apicred.get('api_key', apicred.get('apikey'))
    htuser = apicred.get('basicauth', {}).get('user', "")
    htpass = apicred.get('basicauth', {}).get('pass', "")

    # Construct the url
    server = apicred.get('server', apicred.get('url'))
    if not server.startswith("http"):
        server = "https://" + server
    if server.endswith("/"):
        server = server[:-1]
    if urlsuffix.startswith("/"):
        urlsuffix = urlsuffix[1:]
    url = server + "/" + urlsuffix

    headers = {
        'accept': 'application/json',
        'X-API-Key': apikey,
    }

    msg += f"Calling URL: {url}" + "\n"
    if (htuser == '') and (htpass == ''):
        response = requests.get(url,
                                headers=headers,
                                verify=False,
                                timeout=10)
    else:
        response = requests.get(url,
                                headers=headers,
                                auth=HTTPBasicAuth(htuser, htpass),
                                verify=False,
                                timeout=10)
    is_valid = True if response.status_code == 200 else False
    msg += f"Response: {response.reason}" + "\n"

    return is_valid, response, msg


def load_profile_api(args, spec_category):
    msg = ""

    # API endpoint for anomalies service
    apicred = args['apicred']
    urlsuffix = f"/api/v2/dashboard/specs/"
    is_valid, response, l_msg = call_api(apicred, urlsuffix=urlsuffix)
    msg += l_msg
    if not is_valid:
        return is_valid, None, msg

    # now, loop through to get the app name
    app_name = None
    specs = []
    jdata = response.json()['data']
    for app_id, app_spec in jdata.items():
        if app_id == spec_category:
            for app in app_spec:
                app_name = app['name'] # for now, use the last app, generalize later

                # now, get the specs from the app
                app_name_url = spec_category.split('.')[-1]
                urlsuffix = f"/api/v2/app/{app_name_url}/{urllib.parse.quote(app_name)}/policies"
                is_valid, response, l_msg = call_api(apicred, urlsuffix)
                msg += l_msg
                if not is_valid:
                    continue
                    # return None, is_valid, msg

                specs += response.json()['data']

    profile = {
        "specs": specs
    }

    return is_valid, profile, msg

def get_profile_from_api(clsobj, spec_category):
    """
    Read the profile json from API
    """

    msg = ""

    if (not hasattr(clsobj, "args")):
        raise Exception(
            "'args' transform attribute should be defined"
        )
    for p in ['apicred']:
        if clsobj.args.get(p) == None:
            raise Exception(
                f"'{p}' attribute in args should be defined"
                )

    # call the API to get the anomaly specs
    msg += f"Loading profile from API" + "\n"
    is_valid, profile, l_msg = load_profile_api(clsobj.args, spec_category)
    msg += l_msg

    if 'specs' in profile:
        msg += f"Found {len(profile['specs'])} policies for spec: {spec_category}" + "\n"
    else:
        msg += f"Could not find 'specs' in the API response"

    return is_valid, profile, msg


###############################
# File based profile
###############################
def get_profile_from_file(clsobj):
    """
    Read the profile json from profilespec
    """

    is_valid = True
    msg = ""

    if (not hasattr(clsobj, "profiledir")) and (not hasattr(clsobj, "profilefile")):
        raise Exception(
            "'profiledir' transform attribute should be defined to use default get_profile method"
        )

    paths = []
    if hasattr(clsobj, "profilefile"):
        paths.append(self.profilefile)

    if hasattr(clsobj, "profiledir"):
        paths.extend(
            [
                clsobj.profiledir + "/profile.json",
                clsobj.profiledir + "/profile.yaml",
                clsobj.profiledir + "/profilespec.json",
                clsobj.profiledir + "/profilespec.yaml",
                clsobj.profiledir + "/profilespec.py",
            ]
        )

    profile = None
    for p in paths:
        if not os.path.exists(p):
            continue
        if p.endswith(".json"):
            profile = json.load(open(p))
        elif p.endswith(".yaml"):
            profile = yaml.load(open(p))
        elif p.endswith(".py"):
            # => Load from the file...
            libname = str(clsobj) + "_profile"
            spec = importlib.util.spec_from_file_location(libname, p)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            if hasattr(foo, 'get_profile'):
                profile = foo.get_profile()
            elif hasattr(foo, 'get_profile_spec'):
                profile = foo.get_profile_spec()
            elif hasattr(foo, 'profile'):
                profile = foo.profile

    if profile is None:
        raise Exception("Profile could not be found")

    return is_valid, profile, msg


###############################
# DB handlers
###############################


###############################
# Dataset handlers
###############################
def construct_dataset_list(clsobj, specs):
    if not hasattr(clsobj, 'get_dataset_registry'):
        raise Exception(
            "get_datasets expects get_dataset_registry method"
        )

    # call the overloaded method to get the dataset registry
    registry = clsobj.get_dataset_registry()

    # what are all the datasets in the spec
    spec_datasets = []
    for spec in specs:
        type = spec.get('config', {}).get('source', {}).get('type')
        dataset = spec.get('config', {}).get('source', {}).get('dataset')
        if type != 'registry':
            continue
        if dataset == None:
            continue
        spec_datasets.append(dataset)

    # iterate to keep only the datasets in the spec
    datasets = {}
    for dataset in registry.datasets:
        name = dataset.name
        for subset in dataset.subsets:
            d = f"{name}-{subset['name']}"
            if d in spec_datasets:
                # make a lookup table
                datasets[d] = dataset

    return datasets
