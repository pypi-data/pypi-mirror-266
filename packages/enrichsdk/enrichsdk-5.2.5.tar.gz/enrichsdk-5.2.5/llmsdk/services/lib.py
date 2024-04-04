import os
import sys
import json
import re
import hashlib
import pickle
import logging
import operator
import glob
import struct
import traceback
import threading
import time
from datetime import datetime
from collections import Counter, defaultdict
from asgiref.sync import async_to_sync, sync_to_async

from fastapi import FastAPI, BackgroundTasks, Depends

from ..lib import SafeEncoder, slugify
from .log import *

logger = get_logger()

##########################
# Global variables
##########################
stats = {
    "datasets": {}
}
agents = {}
cache = {}

####################
# Helper functions..
#####################
def get_stats():
    return stats

def get_agents():
    return agents

def get_cache():
    return cache

def initialize_stats():

    now = datetime.now().replace(microsecond=0).isoformat()
    stats.update({
        "pid": os.getpid(),
        "cmdline": " ".join(list(sys.argv)),
        "data_root": os.environ['DATA_ROOT'],
        "run_dir": os.environ['RUNDIR'],
        'when': now,
        "datasets": {},
        'query_count': 0,
        'query_success': 0,
        'query_failure': 0,
    })

def get_files(fullpath, exts):

    total = 0
    stats = defaultdict(int)
    files = defaultdict(list)
    for ext in exts:
        pattern = f"{fullpath}/**/*.{ext}"
        inc = glob.iglob(pattern, recursive=True)
        for f in inc:
            if os.path.isfile(f):
                filesize = os.path.getsize(f)
                print(f, filesize)
                if ((ext in ['sqlite', 'db']) or (filesize < (25 * 10**6))): # 10MB
                    files[ext].append(f)
                    stats[ext] += 1
                else:
                    stats[f'{ext}-ignored'] += 1
                stats['total'] += 1
            else:
                stats[f'{ext}-dir'] += 1

    return stats, files


def get_dir_sha1(dir_root, extra=None):

    # Compute a hash of the directory and return its md5 sum

    sha1hash = hashlib.sha1()
    if extra is not None:
        sha1hash.update(bytes(json.dumps(extra), 'utf-8'))

    for dirpath, dirnames, filenames in os.walk(dir_root, topdown=True):

        dirnames.sort(key=os.path.normcase)
        filenames.sort(key=os.path.normcase)

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            # 1) filename (good idea)
            sha1hash.update(bytes(os.path.normcase(os.path.relpath(filepath, dir_root)), 'utf-8'))

            # 2) mtime (possibly a bad idea)
            st = os.stat(filepath)
            sha1hash.update(struct.pack('d', st.st_mtime))

            # 3) size (good idea perhaps)
            sha1hash.update(bytes(st.st_size))

    return sha1hash.hexdigest()

#####################################################
# Deprecated...
#####################################################
def read_agent_pickle(name):

    logger.warning("Pickling of agent is deprecated")

    run_root = os.environ['RUNDIR']
    agentname = os.environ.get('AGENTNAME',"default")

    # See if there is a pickle file from the past
    pickledir = os.path.join(run_root, "pickles", agentname)
    try:
        os.makedirs(pickledir)
    except:
        pass
    picklefile = os.path.join(pickledir, f"{name}.pkl")
    if os.path.exists(picklefile):
        try:
            data = pickle.load(open(picklefile, 'rb'))
            logger.info(f"Read agent pickle for {name} from {picklefile}")
            return data
        except:
            logger.exception(f"Failed to read pickle for {name}")

    return None

def write_agent_pickle(name, obj):

    logger.warning("Pickling of agent is deprecated")

    run_root = os.environ['RUNDIR']
    agentname = os.environ.get('AGENTNAME',"default")

    # See if there is a pickle file from the past
    pickledir = os.path.join(run_root, "pickles", agentname)
    try:
        os.makedirs(pickledir)
    except:
        pass
    picklefile = os.path.join(pickledir, f"{name}.pkl")
    try:
        with open(picklefile, 'wb') as fd:
            pickle.dump(obj, fd,
                        protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"wrote agent pickle for {name} at {picklefile}")
    except:
        logger.exception(f"Failed to write pickle for {name}")


#####################################################
# Agent details...
#####################################################
def get_llm_cascade():
    llm_cascade = [
        {"id": "economy", "platform": "openai", "model": "gpt-3.5-turbo"},
        {"id": "power", "platform": "openai", "model": "gpt-4"},
    ]
    return llm_cascade

async def get_generic_agent(agentcls,
                            dataset,
                            fullpath,
                            files,
                            metadata,
                            drop_index=False):
    """
    Instantiates the agent.

    Parameters
    ----------
    agentcls: class
              Agent class
    dataset: str
             Name of the dataset
    fullpath: str
              Root directory on the filesystem of dataset
    files: list
           Files within the directory

    Returns
    -------
    status: dict
            Return a diction with agent instance, path of vector index on disk and name of the index
    """

    logger.debug("Using Generic Agent")

    name = os.environ.get('AGENTNAME',"default")
    index_name=slugify(f"{dataset}_index")
    index_path = os.path.expandvars(f"$RUNDIR/$AGENTNAME/index/{dataset}/chromadb_index")
    stats = defaultdict(int)

    agent = agentcls(name=name, cred={})

    try:
        if os.path.exists(index_path) and not drop_index:
            print(f"Loading existing index {name}")
            agent.load_index(store="chroma",
                             persist_directory=index_path,
                             index_name=index_name)
            logger.debug(f"Loaded index: {name}",
                         extra={
                             "data": json.dumps({
                                 'source': 'service',
                                 'user': 'all',
                                 'dataset': dataset,
                                 'stats': agent.get_index_stats()
                             }, indent=4, cls=SafeEncoder)
                         })

            return {
                'agent': agent,
                'index_path': index_path,
                'index_name': index_name
            }

    except:
        logger.exception(f"Failed to load index: {name}")

    print(f"Building new index {name}")
    logger.debug(f"Building a new index",
                 extra={
                     "data": json.dumps({
                         'source': 'service',
                         'user': 'all',
                         'dataset': dataset,
                         'data': index_path
                     },  indent=4, cls=SafeEncoder)
                 })

    first = True
    for ext, extfiles in files.items():

        params = {}
        if ext == "pdf":
            params['pdfloader'] = "pymupdf"

        for f in extfiles:

            # Load data...
            data = None
            try:
                if ext == "pdf":
                    data = agent.load_data(source='pdf',
                                           content=f,
                                           params={
                                               "pdfloader": "pymupdf"
                                           })
                    stats[f'{ext}-mupdf'] +=1
                elif ext in ["doc", "docx"]:
                    data = agent.load_data(source='docx', content=f,)
                    stats[f'{ext}-default'] +=1
                else:
                    data = agent.load_data(source='dir',
                                           content=os.path.dirname(f),
                                           params={
                                               "glob": os.path.basename(f)
                                           })
                    stats[f'{ext}-dirload'] +=1
            except:
                traceback.print_exc()
                stats[f'{ext}-error'] += 1

            if data is None:
                continue

            if first:
                print(f"Creating new index: {name}")
                agent.create_add_index(data=data,
                                       store="chroma",
                                       persist_directory=index_path,
                                       index_name=index_name)
                first = False
            else:
                agent.add_to_index(data=data)

    print(f"Loaded agent {name}")
    logger.debug(f"Loaded agent",
                 extra={
                     "data": json.dumps({
                         'source': 'service',
                         'user': 'all',
                         'dataset': dataset,
                         'stats': agent.get_index_stats()
                     }, indent=4, cls=SafeEncoder)
                 })

    return {
        'agent': agent,
        'index_path': index_path,
        'index_name': index_name
    }

async def get_agent_details(namespace,
                            username,
                            subdir,
                            exts,
                            get_task_specific_agent,
                            force=False,
                            extra=None):
    """
    Check agent cache and return if it exists. Else instantiate an agent. Updates the statisics as well

    Parameters
    ----------
    namespace: str
               Enable instantiating the agent multiple times using a namespace string
    subdir: str
            Subdirectory within the DATA_ROOT environment variable
    username: str
              Name of the user. Each user has a separate instance
    exts: list
           List of extensions
    get_task_specific_agent: callable
           Callback to instantiate an agent

    Returns
    -------
    status: dict
            Return a diction with agent instance, path of vector index on disk and name of the index
    """

    label = f"{username}_{subdir}"
    now = datetime.now().replace(microsecond=0).isoformat()

    run_root = os.environ['RUNDIR']
    dir_root = os.environ['DATA_ROOT']
    fullpath = os.path.join(dir_root, namespace, subdir)
    cred = {}

    # Add a check here to see if something has changed...
    reindex = os.path.join(fullpath, '.reindex')
    print("Reindex check", reindex)
    if os.path.exists(reindex):
        print("Document set changed. So indexing again")
        force = True

    if ((label in agents) and (not force)):
        logger.debug(f"[{namespace}] Returning existing instance",
                     extra={
                         'source': 'service',
                         'user': username,
                         'dataset': subdir
                     })
        return agents[label]

    try:

        if ((label in stats['datasets']) and (not force)):
            logger.debug(f"Return existing agent",
                         extra={
                             'source': 'service',
                             'user': username,
                             'dataset': subdir,
                             'data': json.dumps(stats['datasets'][label],
                                                indent=4,
                                                cls=SafeEncoder)
                         })
        else:
            logger.debug(f"Creating agent (Force: {force})",
                         extra={
                             'source': 'service',
                             'user': username,
                             'dataset': subdir,
                             'data': fullpath
                         })

        if not os.path.isdir(fullpath):
            logger.debug(f"Could not find data",
                         extra={
                             'source': 'service',
                             'user': username,
                             'dataset': subdir,
                             'data': fullpath
                         })
            return None

        # Compute the sha1
        sha1 = get_dir_sha1(fullpath, extra)

        stats['datasets'][label] = {
            'sha1': sha1,
            'loaded': now,
            'username': username,
            'subdir': subdir,
            'fullpath': fullpath,
            'agent_created': False,
            'agent_status': "initialization",
            "query_count": 0,
            "query_success": 0,
            "query_failure": 0,
        }

        filestats, files = get_files(fullpath, exts)

        logger.debug(f"Dataset details",
                     extra={
                         'source': 'service',
                         'user': username,
                         'dataset': subdir,
                         'data': json.dumps({
                             "filestats": filestats,
                             "files": files
                             }, indent=4)
                         })

        if filestats['total'] == 0:
            logger.warning(f"No data found",
                           extra={
                               'source': 'service',
                               'user': username,
                               'dataset': subdir,
                        })

            stats['datasets'][label]['agent_status'] = f"Error! Files not found"
            return None

        # Include the metadata
        metadatapath = os.path.join(fullpath, 'metadata.json')
        print("metadatapath", metadatapath)

        metadata = {}
        if os.path.exists(metadatapath):
            try:
                metadata = json.load(open(metadatapath))
            except:
                logger.exception(f"Failed to read metadata",
                                 extra={
                                     'source': 'service',
                                     'user': username,
                                     'dataset': subdir,
                                     'data': metadatapath
                                 })


        stats['datasets'][label].update({
            'filestats': filestats,
            "files": files,
            "metadata": metadata
        })


        agentdetails = await get_task_specific_agent(namespace,
                                                     username,
                                                     subdir,
                                                     fullpath,
                                                     files,
                                                     metadata,
                                                     drop_index=force)

        if agentdetails is None:
            raise Exception("Task specific agent returned invalid details")


        stats['datasets'][label].update({
            'agent_created': True,
            "agent_status": "Created"
        })

        agents[label] = {
            'sha1': sha1,
            'created': now,
            "metadata": metadata
        }

        agents[label].update(agentdetails)

        stats['datasets'][label]['agent_status'] = f"Ready!"
        logger.debug(f"Agent is ready!",
                       extra={
                           "data": {
                               'source': 'service',
                               'user': username,
                               'dataset': subdir,
                               'data': metadatapath
                           }
                       })

        if os.path.exists(reindex):
            os.remove(reindex)

    except Exception as e:
        logger.exception(f"Failed to build agent",
                       extra={
                           "data": {
                               'source': 'service',
                               'user': username,
                               'dataset': subdir,
                           }
                       })

        stats['datasets'][label]['agent_created'] = False
        stats['datasets'][label]['agent_status'] = f"Error! {e}"
        return None

    return agents[label]


async def check_agent_details(username, subdir):
    label = f"{username}_{subdir}"
    return label in agents

###########################################################
# Build tasks..
###########################################################

buildtasks = {}
def get_buildtask_details(label):
    return buildtasks.get(label, None)

def add_buildtask(label, params):

    if label not in buildtasks:
        condition.acquire()
        buildtasks[label] = params
        condition.release()
        msg = "Started indexing documents in the background and creating an agent"
    else:
        status = buildtasks[label]['status']
        if status == "tobuild":
            msg = 'Index is being built. Wait'
        elif status == "failure":
            msg = 'Index could not be built. See log'
        elif status == "success":
            msg = 'Index has been built. Use force is rebuild'
        else:
            msg = 'Status of index is unknown. Could be an internal error. Check log'

    return msg

condition = threading.Condition()
class BuildAgentThread(threading.Thread):

    #Background job that is continuously building the indexes
    #required

    def __init__(self, agentfunc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agentfunc = agentfunc

    def run(self, *args,**kwargs):
        global buildtasks

        agentfunc = self.agentfunc

        logger.debug(f"Index builder thread Start {id(buildtasks)}")
        while True:
            for label in list(buildtasks.keys()):
                params = buildtasks[label]
                status = params.get('status','unknown')
                force = params.get('force', False)
                if ((status == "tobuild") or (force)):
                    logger.debug(f"Building index for {label} (force={force})")
                    try:
                        details = async_to_sync(get_agent_details)\
                            (namespace=params['namespace'],
                             username=params['user'],
                             subdir=params['dataset'],
                             exts=params['exts'],
                             get_task_specific_agent=agentfunc,
                             force=force)

                        status = "failure" if details is None else "success"
                        message = "Regular execution"
                        logger.debug(f"Index Build: {status}",
                                     extra={
                                         "source": "service",
                                         'user': params['user'],
                                         "dataset": params['dataset'],
                                         "data": json.dumps(params, indent=4, cls=SafeEncoder)
                                     })
                    except Exception as e:
                        logger.exception(f"Index Build: failure",
                                         extra={
                                             "source": "service",
                                             'user': params['user'],
                                             "dataset": params['dataset'],
                                             "data": json.dumps(params, indent=4, cls=SafeEncoder)
                                         })
                        status = "failure"
                        message = f"Exception {str(e)}"

                    condition.acquire()
                    params['status'] = status
                    params['message'] = message
                    condition.release()

            time.sleep(0.1)

#####################################################
# Helper functions
#####################################################
def add_show_cache(app):

    @app.get("/cache")
    def show_cache():
        """
        Summarize the cache
        """

        cache = get_cache()
        summary = defaultdict(int)
        for k, v in cache.items():
            summary[v['status']] += 1

        return summary

def add_show_health(app):

    @app.get("/health")
    def show_health():
        """
        Return the stats
        """
        logger.info("Returning stats",
                    extra={
                        "source": "service"
                    })
        return stats

def add_build_index(app, namespace_default, exts):

    @app.get("/index/build")
    async def build_index(user: str,
                          dataset: str,
                          background_tasks: BackgroundTasks,
                          namespace=namespace_default,
                          force=False
    ):

        label = f"{user}_{dataset}"

        params = {
            "status": "tobuild",
            "user": user,
            "dataset": dataset,
            "namespace": namespace,
            "exts": exts
        }

        # => Insert it into the build tasks if not already indexed...
        msg = add_buildtask(label, params)

        logger.debug(msg,
                     extra={
                         "source": "service",
                         "user": user,
                         "dataset": dataset,
                     })
        return {
            'status': 'success',
            'message': msg
        }

def add_check_index(app, namespace_default):

    @app.get("/index/check")
    async def check_index(user: str,
                          dataset: str,
                          namespace=namespace_default
    ):
        """
        Check build tasks
        """

        label = f"{user}_{dataset}"
        try:

            params = buildtasks.get(label,{})
            status = params.get('status', 'unknown')
            if len(params) == 0:
                msg = "Does not exist"
            elif status == "success":
                msg = 'Exists'
            else:
                msg = "Does not exist"
            logger.debug(f"Index check: {status}",
                         extra={
                             "source": "service",
                             "user": user,
                             "dataset": dataset,
                        })

            return {
                'status': 'success',
                'message': msg
            }
        except Exception as e:
            logger.exception(f"Index check: Failed.",
                             extra={
                                 "source": "service",
                                 "user": user,
                                 "dataset": dataset,
                             })
            return {
                'status': 'failure',
                'message': f"Internal error: {str(e)}"
            }



def query_update_result(request_id, result):

    # First get the params
    cache = get_cache()
    value = cache[request_id]

    for k, v in result.items():
        value[k] = result[k]

    status = result.get('status', 'unknown')
    logger.debug(f"Updated Result: {status}",
                extra={
                    "source": "service",
                    "request_id": request_id,
                    "user": value.get("user", "unknown"),
                    "dataset": value.get("dataset", "unknown"),
                    'data': json.dumps(result, indent=4, cls=SafeEncoder)
                })

###############################################
#
###############################################
def add_policy(app, policyspec):

    @app.get("/policy")
    def show_policy():
        """
        Return the stats
        """

        logger.info("Returning policy",
                    extra={
                        "source": "service"
                    })
        return {
            "status": "success",
            "data": policyspec
        }
