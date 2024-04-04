import os
import json
import copy
import re
import logging
import traceback
import importlib
import subprocess
import base64
import inspect
import shutil
from datetime import datetime
from dateutil import parser as dateparser
from dateutil.tz import tzlocal
from colored import fg, bg, attr
from cryptography.fernet import Fernet

from .exceptions import *
from .context import *
from .resources import *

logger = logging.getLogger("app")

def greenbg(txt):
    return "{} \u2713 {} {}".format(bg("light_green"), txt, attr(0))


def redbg(txt):
    return "{} \u274C {} {}".format(bg("indian_red_1a"), txt, attr(0))


def orangebg(txt):
    return "{} \u0023 {} {}".format(bg("dark_orange_3a"), txt, attr(0))


cached_siteconf = {}
cached_versionmap = {}

# Have we already warned the user about over-rides
warned_overrides = False

def write_unencrypted_creds(creds, encfile=None):

    if encfile is None:
        etcdir = os.environ.get("ENRICH_ETC", os.path.join(os.environ.get("ENRICH_ROOT"), "etc"))
        filename = os.path.join(etcdir, "sitecred.json")
    else:
        filename = encfile

    with open(filename + ".new", "w") as fd:
        fd.write(json.dumps(creds, indent=4))

    # Now move it to the right place
    shutil.move(filename + ".new", filename)


def write_encypted_creds(key, creds, encfile=None):

    key = base64.urlsafe_b64encode(key[:32].encode("utf-8"))
    f = Fernet(key)

    # Turn into text
    content = json.dumps(creds)

    # Encrypt
    contentb= f.encrypt(content.encode("utf-8"))

    # Where should I put this?
    if encfile is None:
        etcdir = os.environ.get("ENRICH_ETC", os.path.join(os.environ.get("ENRICH_ROOT"), "etc"))
        filename = os.path.join(etcdir, "sitecred.enc")
    else:
        filename = encfile

    with open(filename + ".new", "wb") as fd:
        fd.write(contentb)

    # Now move it to the right place
    shutil.move(filename + ".new", filename)

def read_unencrypted_creds(key, encfile=None):

    # Where should I put this?
    if encfile is None:
        etcdir = os.environ.get("ENRICH_ETC", os.path.join(os.environ.get("ENRICH_ROOT"), "etc"))
        filename = os.path.join(etcdir, "sitecred.json")
    else:
        filename = encfile

    if not os.path.exists(filename):
        return {}

    return json.load(open(filename))

def read_encrypted_creds(key, encfile=None):

    # Where should I put this?
    if encfile is None:
        etcdir = os.environ.get("ENRICH_ETC", os.path.join(os.environ.get("ENRICH_ROOT"), "etc"))
        filename = os.path.join(etcdir, "sitecred.enc")
    else:
        filename = encfile

    if not os.path.exists(filename):
        return {}

    key = base64.urlsafe_b64encode(key[:32].encode("utf-8"))
    f = Fernet(key)

    try:
        with open(filename, "rb") as fd:
            contentb = fd.read()
            content = f.decrypt(contentb)
            params = json.loads(content)
    except:
        logger.error("Failed to read sitecred.enc")
        params = {}

    return params

def read_siteconf_json(filename, app={}, context={}):

    global cached_siteconf

    try:
        # Try the sitelib first.
        import sitelib

        # Return cached file
        if filename in cached_siteconf:
            return cached_siteconf[filename]

        nature, siteconf = sitelib.read_siteconf(filename, app)
        if siteconf is None:
            raise Exception("Failed to read siteconf")

        # Cache it
        cached_siteconf[filename] = siteconf
        if nature == "open":
            logger.warning("Successfully read siteconf but it is insecure")
        else:
            logger.warning("Successfully read secure siteconf")
    except:
        # sitelib may not be installed
        # logger.debug("Could not read secure siteconf. Falling back")
        try:
            # If this is a jsonx file, then try the json version of
            # the file.
            if filename.endswith("jsonx"):
                filename = filename.replace("jsonx", "json")
            siteconf = json.load(open(filename))
            cached_siteconf[filename] = siteconf
        except:
            traceback.print_exc()
            siteconf = None

    if siteconf is None:
        raise Exception("Could not read siteconf")

    if not isinstance(siteconf, dict):
        raise Exception(
            "Invalid siteconf found. Expecting 'dict' found '{}'".format(
                str(type(siteconf))
            )
        )

    return siteconf


def read_siteconf_obs(filename=None, app={}, context={}):

    # If context not available, then generate it.
    if len(context) == 0:
        context = Context().asdict()

    # This overrides everything else...
    if "ENRICH_SITECONF" in os.environ:
        try:
            import sitelib

            encoded = os.environ["ENRICH_SITECONF"]
            confbytes = base64.b64decode(encoded)
            siteconf = sitelib.decode_bytes(confbytes)
            siteconf = json.loads(siteconf)
            return siteconf
        except:
            pass

    if filename is not None:
        return read_siteconf_json(filename, app)

    tries = [
        "siteconf.jsonx",
        "siteconf.json",
        "etc/siteconf.jsonx",
        "etc/siteconf.json",
        "enrich/etc/siteconf.jsonx",
        "enrich/etc/siteconf.json"
    ]
    try:
        tries.extend(
            [
                "%(ENRICH_ETC)s/siteconf.jsonx" % context,
                "%(ENRICH_ETC)s/siteconf.json" % context,
            ]
        )
    except:
        pass

    tries.extend(
        [
            os.path.expandvars("${ENRICH_ETC}/siteconf.jsonx"),
            os.path.expandvars("${ENRICH_ETC}/siteconf.json"),
        ]
    )

    siteconf = None
    for filename in tries:
        if os.path.exists(filename):
            siteconf = read_siteconf_json(filename, app, context)
            if siteconf is None:
                continue
            else:
                break

    if siteconf is None:
        logger.warning(
            "Could not find siteconf. Using empty dict"
        )

        siteconf = {
            'credentials': {}
        }

    # Now load the encrypted

    return siteconf

def read_siteconf(filename=None, app={}, context={}):

    # Read the default
    siteconf = read_siteconf_obs(filename, app, context)

    if (("DJANGO_SECRET_KEY" not in os.environ) and
        ("SECRET_KEY" not in os.environ)):
        return siteconf

    try:

        if "SECRET_KEY" in os.environ:
            key = os.environ['SECRET_KEY']
        else:
            key = os.environ['DJANGO_SECRET_KEY']

        #=> Try the encrypted file first. Otherwise fall back on the
        # unencrypted
        try:
            encsiteconf = read_encrypted_creds(key)
        except:
            encsiteconf = read_unencrypted_creds()

        if len(encsiteconf) == 0:
            return siteconf

        # => First incorporate the credentials
        if 'credentials' in encsiteconf:
            creds = encsiteconf['credentials']
        else:
            creds = encsiteconf
        default = siteconf.pop('credentials', {})
        overrides = []
        for k, v in creds.items():
            if k in default:
                overrides.append(k)
            default[k] = v
        siteconf['credentials'] = default

        # Next include the timezone and such
        if 'timezone' in encsiteconf:
            siteconf['timezone'] = encsiteconf['timezone']
            overrides.append('timezone')

        if 'dashboard' in encsiteconf:
            for k, v in encsiteconf['dashboard'].items():
                siteconf['dashboard'][k] = v
                overrides.append(k)

        if 'envvars' in encsiteconf:
            encvariables = encsiteconf['envvars']
            if not isinstance(encvariables, dict):
                encvariables = {}
            variables = siteconf.get('variables', {})
            for k, v in encvariables.items():
                variables[k] = v
                overrides.append(k)
            siteconf['variables'] = variables

        # Note any overrides
        if len(overrides) > 0:
            global warned_overrides
            if not warned_overrides:
                logger.warning("Overriding credentials from sitecred",
                               extra={
                                   'data': ", ".join(overrides)
                               })
                warned_overrides = True

    except:
        traceback.print_exc()
        logger.error("Error while reading sitecred")

    return siteconf


def get_credentials(siteconf, name):
    """
    Look up the credentials file
    """

    if (siteconf is None) or (not isinstance(siteconf, dict)):
        raise Exception("Invalid siteconf - None or has invalid datatype")

    if ("credentials" not in siteconf) or (name not in siteconf["credentials"]):
        raise Exception("missing credentials")

    return siteconf["credentials"][name]


def get_credentials_by_name(name, app={}, context={}):
    """
    Lookup credentials by name
    """

    siteconf = read_siteconf(app=app, context={})
    return get_credentials(siteconf, name)


def get_credentials_by_type(conditions, app={}, context={}):
    """
    Lookup credentials by type
    """

    siteconf = read_siteconf(app=app, context={})

    if (siteconf is None) or (not isinstance(siteconf, dict)):
        raise Exception("Invalid siteconf - None or has invalid datatype")

    if "credentials" not in siteconf:
        raise Exception("missing credentials")

    if not isinstance(conditions, dict):
        raise Exception("Invalid condition specification")

    final = {}
    for name, detail in siteconf["credentials"].items():

        if not isinstance(detail, dict):
            continue

        if not detail.get("enable", True):
            continue

        match = True
        for var, choices in conditions.items():
            if var not in detail:
                match = False
                break
            if detail[var] not in choices:
                match = False
                break

        if not match:
            continue

        final[name] = copy.deepcopy(detail)

    return final

############################################
# Access emails
############################################
def get_siteconf_var(var, section=None, default=None):

    siteconf = read_siteconf()

    if ((section in siteconf) and
        (isinstance(siteconf[section], dict))):
        return siteconf[section].get(var, default)

    return siteconf.get(var, default)

def get_env_var(var, default=None, debug=False):
    """
    Get variable from environment. Account for
    """
    varlist = []
    if isinstance(var, list):
        varlist = var
    else:
        varlist = [str(var)]

    if debug:
        print("varlist", varlist)

    siteconf = read_siteconf()

    if debug:
        print(siteconf.get('variables', {}))
    variables = siteconf.get('variables', {})
    for var in varlist:
        if var in variables:
            if debug:
                print("Found in siteconf", var, "with value", variables[var])
            return variables[var]

    for var in varlist:
        if var in os.environ:
            if debug:
                print("Found in env", var, "with value", os.environ[var])
            return os.environ[var]

    return default

def get_env_var_list(var, separator=",", default=[]):

    value = get_env_var(var)
    if not isinstance(value, str):
        return default

    values = value.split(separator)
    values = [v for v in values if len(v) > 0]
    return values

def get_env_var_bool(var, default=False):

    value = get_env_var(var)
    if not isinstance(value, str):
        return default

    return value.lower().strip() == 'true'

def get_default_from_email(name='from'):
    """
    Get default emails
    """

    siteconf = read_siteconf()
    notification = siteconf.get('notification', {})
    if name in notification:
        return notification[name]

    email = get_env_var(['DJANGO_DEFAULT_FROM_EMAIL',
                        'DEFAULT_FROM_EMAIL'],
                        default='Scribble Support<support@scribbledata.io>')

    return email

def update_from_git(detail, context, debug=False):

    # Make a local version
    context = copy.copy(context)

    label = detail.get("label", detail.get("repo", "unknown"))

    # Try the detail run root
    root = detail["git"] % context
    if not os.path.exists(root):

        # try one alternative path if possible
        if "ENRICH_RUN_ROOT" not in detail["git"]:
            raise Exception("Expected ENRICH_RUN_ROOT: {}".format(detail["git"]))

        # Fallback to the default run_root
        context["ENRICH_RUN_ROOT"] = context["ENRICH_ROOT"]
        altroot = detail["git"] % context
        if not os.path.exists(altroot):
            raise Exception("Missing repo roots: {}, {}".format(root, altroot))
        root = altroot

    # Update in place
    detail["git"] = root

    # By default use master branch only..
    branch = detail.get("branch", "master")

    # Collect all the notes
    # Guard the path as it could contain spaces in Windows
    cmd = "git -C \"{}\" log {} --pretty='%h--%ci--%N'".format(root, branch)
    notes = subprocess.check_output(cmd, shell=True)
    notes = notes.decode("utf-8")
    notes = notes.split("\n")
    notes = [
        n.split("--") for n in notes if (n.count("--") == 2 and not n.endswith("--"))
    ]  # remove empty

    detail["notes"] = [
        {"commit": n[0], "commit_date": n[1], "message": n[2]} for n in notes
    ]

    # => Collect branches..
    # Guard the path as it could contain spaces in Windows
    cmd = """git -C "{}" branch -l""".format(root)
    lines = subprocess.check_output(cmd, shell=True)
    lines = lines.decode("utf-8")
    lines = lines.split("\n")
    lines = [l[2:] for l in lines]
    detail["branches"] = lines

    # Collect the git commits
    # Guard the path as it could contain spaces in Windows
    cmd = """git -C "{}" log {} --no-walk --tags --all --pretty="%h\t%D\t%ce\t%ci\t%s" --decorate=full --date=short""".format(
        root, branch
    )
    lines = subprocess.check_output(cmd, shell=True)
    lines = lines.decode("utf-8")
    lines = lines.split("\n")
    lines = [l.strip() for l in lines]
    lines = [l.split("\t") for l in lines]
    lines = [l for l in lines if len(l) == 5]
    alltags = []
    for l in lines:

        if debug:
            print(l)

        # Skip all irrelevant remotes except upstream for the given branch
        refs = [x.strip() for x in l[1].split(",")]

        # Use relevant records. There is stuff from other branches,
        valid = False
        for r in refs:
            if (
                ("refs/heads/{}".format(branch) in r)
                or ("refs/remotes/origin/{}".format(branch) in r)
                or ("refs/tags" in r)
                or ("HEAD" in r)
            ):
                if debug:
                    print("Match", r)
                valid = True
                break

        if not valid:
            if debug:
                print("Skipping")
            continue

        # Is this head?
        head = any([ref.startswith("HEAD") for ref in refs])

        # Align the local date
        try:
            dt = dateparser.parse(l[3]).astimezone(tzlocal()).isoformat()
        except:
            dt = l[3]

        entry = {
            # ['416366c', 'tag: refs/tags/v1.4.0, refs/heads/master', '2020-03-03', 'pingali@gmail.com', 'Bug']
            "commit": l[0],
            "refs": refs,
            "author": l[2],
            "date": dt,
            "log": l[4],
        }

        # Extract the tag for this commit
        for ref in refs:
            match = re.search(r"tag: refs/tags/(\S+)", ref)
            if match is not None:
                tag = match.group(1)
                entry["tag"] = tag
                break

        if "tag" not in entry:
            entry["tag"] = l[0]

        if debug:
            print(entry)

        alltags.append(entry)

    # Now sort by reverse commit date
    alltags = sorted(alltags, key=lambda entry: entry["date"], reverse=True)
    detail["alltags"] = alltags

    position = "post"
    for entry in alltags:

        head = any([ref.startswith("HEAD") for ref in entry["refs"]])

        # Where is this position...
        if head:
            entry["position"] = "head"
            position = "pre"
        else:
            entry["position"] = position

        if head:
            detail["release"] = entry["tag"]
            detail["commit"] = entry["commit"]
            detail["date"] = entry["date"]

            # Insert the URL as well
            if (("url" in detail) and ("tree" in detail['url'])):
                urlparts = detail["url"].split("/")
                urlparts[-1] = detail["commit"]
                url = "/".join(urlparts)
                detail["url"] = url


def update_from_package(detail, context):

    pkgname = detail["package"]
    mod = importlib.import_module(pkgname)

    # v0.4.3+0.g659ce50.dirty
    if not hasattr(mod, "__version_detailed__"):
        return

    pkgdetails = mod.__version_detailed__
    release = pkgdetails["version"]
    commit = pkgdetails["full-revisionid"]

    # Now overwrite the release information
    detail["release"] = release
    detail["commit"] = commit[:8]
    if "url" in detail:
        urlparts = detail["url"].split("/")
        urlparts[-1] = detail["commit"]
        url = "/".join(urlparts)
        detail["url"] = url
    else:
        detail["release"] += " (out of date; version missing)"
        logger.error(
            "VersionMap: Cannot collect version information for {}".format(pkgname),
            extra={"data": json.dumps(detail, indent=4)},
        )

def get_versionmap_from_subdir():

    versionmap = []

    # Check if there are repos that need to be included
    etcdir = os.environ.get("ENRICH_ETC",
                            os.path.join(os.environ.get('ENRICH_ROOT'),
                                         'etc'))
    versiondir = os.path.join(etcdir, "versions")
    if not os.path.exists(versiondir):
        return versionmap

    files = os.listdir(versiondir)
    for f in files:
        fullpath = os.path.join(versiondir, f)
        try:
            versionmap.append(json.load(open(fullpath)))
        except:
            continue

    return versionmap

def get_versionmap_from_code():

    versionmap = []

    try:
        from git import Repo

        # Check if there are repos that need to be included
        customerdir = os.environ.get("ENRICH_CUSTOMERS",
                                     os.path.join(os.environ.get('ENRICH_ROOT'),
                                                  'customers'))
        for c in os.listdir(customerdir):
            repodir = os.path.join(customerdir, c)
            try:
                if not os.path.exists(os.path.join(repodir, ".git")):
                    continue

                repo = Repo(repodir)
                reader = repo.config_reader()
                if not reader.has_section('remote "origin"'):
                    continue
                repodata = dict(reader.items('remote "origin"'))
                {
                    "date": "2019-12-11 15:33:47 +0530",
                    "label": "scribble",
                    "description": "Core scribble applications",
                    "repo": "enrich-scribble",
                    "dynamic": True,
                    "git": "%(ENRICH_RUN_ROOT)s/customers/scribble",
                    "commit": "f58a048d380c911fd2d7bd8fa5909499f8d36c25",
                    "notes": [],
                    "url": "https://github.com/pingali/enrich-scribble/tree/f58a048d380c911fd2d7bd8fa5909499f8d36c25",
                    "release": "v1.0.9"
                },
                branch = repo.active_branch.name
                url = repodata['url']
                if (("https://" in url) and ("@" in url)):
                    url = "https://xxx" + url[url.index("@"):]
                entry = {
                    "label": c,
                    "repo": c,
                    "description": "Unspecified",
                    "branch": branch,
                    "url": url,
                    "git": "%(ENRICH_RUN_ROOT)s/customers/" + c,
                    "dynamic": True,
                }
                versionmap.append(entry)

            except:
                #traceback.print_exc()
                pass
    except:
        pass

    return versionmap

def read_versionmap(filename=None, include_notes=False,
                    include_tags=False, context={},
                    ignore_cache=False):

    global cached_versionmap

    if isinstance(context, dict):
        if len(context) == 0:
            context = Context().asdict()
    elif isinstance(context, Context):
        context = context.asdict()

    default = [
        {
            "repo": "error",
            "release": "v1xxx",
            "date": "2018-10-09 12:06:40 +0530",
            "commit": "5079404f12df939c138215ed1a02e4d0d8814e00",
            "description": "Error while reading the versionmap",
            "url": "https://github.com/pingali/error/commit/5079404f12df939c138215ed1a02e4d0d8814e00",
            "label": "error",
            "notes": [
                {
                    "commit": "6271dcae",
                    "commit_date": "2018-10-09 12:06:40 +0530",
                    "notes": "v0 of the release",
                }
            ],
        }
    ]

    tries = [
        "versionmap.json",
        "etc/versionmap.json",
        "enrich/etc/versionmap.json",
        context.get('versionmap', None),
    ]
    if filename is not None:
        tries.append(filename)
    if "ENRICH_ETC" in context:
        altfilename = "%(ENRICH_ETC)s/versionmap.json" % context
        tries.append(altfilename)
    elif "ENRICH_ETC" in os.environ:
        altfilename = os.path.expandvars("$ENRICH_ETC/versionmap.json")
        tries.append(altfilename)

    selected_filename = None
    for f in tries:
        if ((f is not None) and (os.path.exists(f))):
            selected_filename = f

    now = datetime.now().replace(microsecond=0).isoformat()
    if selected_filename is None:
        error = "Missing versionmap: {}".format(filename)
        logger.error(error)
        default[0]["description"] = error
        return None, default

    # Make the selected filename as default
    filename = selected_filename

    # => use the filename's timestamp as the default timestamp
    timestamp = datetime.fromtimestamp(os.path.getmtime(filename))
    timestamp = timestamp.isoformat()

    if ((filename in cached_versionmap) and (not ignore_cache)):
        return timestamp, cached_versionmap[filename]

    try:
        versionmap = json.load(open(filename))
    except:
        error = "Invalid version file. Not a valid json file: {}".format(filename)
        logger.error(error)
        default[0]["description"] = error
        return default

    # => Newer dict format of the versionmap
    if isinstance(versionmap, dict):
        timestamp = versionmap.get("timestamp", timestamp)
        versionmap = versionmap.get("versionmap", None)

    if not isinstance(versionmap, list):
        error = "Invalid version map. Not a list: {}".format(filename)
        logger.error(error)
        default[0]["description"] = error
        return timestamp, default

    # Insert information from the source repos
    versionmapextra = get_versionmap_from_code()
    for extrav in versionmapextra:
        label = extrav['label']
        found = False
        for v in versionmap:
            if v.get('label', 'unknown') == label:
                found = True
                break
        if found:
            continue
        versionmap.append(extrav)

    #
    versionmapextra = get_versionmap_from_subdir()
    for extrav in versionmapextra:
        label = extrav['label']
        # Replace existing entry with the modified entry
        replaced = False
        cleaned_versionmap = []
        for v in versionmap:
            if v.get('label', 'unknown') == label:
                replaced = True
                cleaned_versionmap.append(extrav)
            else:
                cleaned_versionmap.append(v)

        versionmap = cleaned_versionmap


    # Update the release and commit information if dynamic modules are
    # specified.
    for i in range(len(versionmap)):

        label = versionmap[i].get("label", versionmap[i].get("repo", "unknown"))

        if "branch" not in versionmap[i]:
            versionmap[i]["branch"] = "master"

        if versionmap[i].get("dynamic", False):
            try:
                if "package" not in versionmap[i] and "git" not in versionmap[i]:
                    versionmap[i]["release"] += " (out of date; config issue)"
                    logger.error(
                        "VersionMap: Missing package to be checked",
                        extra={"data": json.dumps(versionmap[i], indent=4)},
                    )
                elif "package" in versionmap[i]:
                    update_from_package(versionmap[i], context)
                elif "git" in versionmap[i]:
                    update_from_git(versionmap[i], context)

            except:
                traceback.print_exc()
                versionmap[i]["release"] += " (out of date; import issue)"
                logger.exception(
                    "{}: Unable to import package/repository to update version".format(
                        label
                    ),
                    extra={"data": json.dumps(versionmap[i], indent=4)},
                )

    # Cleanup of the output
    for i in range(len(versionmap)):

        # Drop the notes by default
        if not include_notes:
            versionmap[i].pop("notes", [])

        if not include_tags:
            versionmap[i].pop("alltags", [])

    # Cache the outputs...
    cached_versionmap[filename] = versionmap

    return timestamp, versionmap
