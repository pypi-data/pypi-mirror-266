"""

This module implements the DataGPT microservice. Its purpose is to wrap
around the DataGPT agent and provide an integration point from end applications.
The DataGPT module enables users to run queries on datasets.

"""
import os
import sys
import re
import glob
import yaml
import json
import traceback
import time
import hashlib
import struct
import logging
import threading
from uuid import uuid4
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi_utils.tasks import repeat_every

from llmsdk.agents.datagpt import LLMDataQuerier
from llmsdk.lib import SafeEncoder

from .log import *
from .lib import *

# Override default uvicorn logger...
logging.config.dictConfig(log_config)
logger = get_logger()

supported_exts = ['csv', 'sqlite']

app = FastAPI()


##############################################
# Common
##############################################
add_show_cache(app)
add_show_health(app)

##############################################
# Policy Code
##############################################
policyspec = [
    {
        "id": 1,
        "name": "filter-by-column-value",
        "description": "Allow filtering on particular column values",
        "params": [
            {
                "name": "column",
                "type": "string",
                "example": "mycolumn",
                "required": True
            },
            {
                "name": "value",
                "type": "string",
                "example": "texas",
                "required": True
            }
        ]
    }
]
add_policy(app, policyspec)

##############################################
# Handlers
##############################################
async def get_datagpt_agent(namespace, username, dataset,
                            fullpath, files,
                            metadata,
                            drop_index=False):

    cascade = get_llm_cascade()

    if 'sqlite' not in files:
        raise Exception("Please check the dataset. Only SQLite files supported for now by datagpt")

    logger.debug("Getting DataGPT agent",
                 extra={
                     "data": "Metadata: " + json.dumps(metadata, indent=4) + "\nFiles: " + str(files)
                 })

    found = False
    for filename in files['sqlite']:
        for details in metadata.get('files', []):
            if ((not isinstance(details, dict)) or
                (len(details) == 0) or
                ('path' not in details) or
                ('tables' not in details)):
                continue

            path = details['path']
            if filename.endswith(path):
                found = True
                tables = details['tables']
                print(f"Found table metadata for {filename}")

    if not found:
        raise Exception(f"Could not find tables metadata for {filename}")

    mode = 'sql'
    data = {
        'mode': mode,
        'dataset': filename,
        'tables': tables
    }

    agent = LLMDataQuerier(name="datagpt",
                           cred=None,
                           mode=mode,
                           data=data,
                           cascade=cascade,
                           debug=True)

    logger.debug(f"Choosing {mode}",
                 extra={
                     "data": json.dumps({
                     "source": "service",
                     'user': username,
                     'dataset': dataset,
                     'files': files
                     }, indent=4, cls=SafeEncoder)
                 })


    return {
        "agent": agent
    }

async def qna_run(request_id):
    """
    Query the agent instance created

    Parameters
    ----------
    request_id: str
                UUID generated for the request

    Returns
    -------
    None
         Nothing is returned. Only the result cache is updated

    """

    cache = get_cache()

    if request_id not in cache:
        logger.error(f"Failure",
                     extra={
                         'request_id': "invalid",
                         "source": "service",
                     })
        cache[request_id] = {
            'status': "failure",
            "message": f"Invalid request id"
        }
        return

    # First get the params
    value = cache[request_id]

    try:

        params  = value['params']
        user    = params['user']
        dataset = params['dataset']
        context = params['context']
        namespace = params['namespace']
        query = params['query']
        mode  = params['mode']

        stats['query_count'] += 1

        label = f"{user}_{dataset}"

        # First get the agent...
        logger.debug(f"Getting agent",
                     extra={
                         "source": "service",
                         "user": user,
                         "dataset": dataset,
                         "request_id": request_id,
                         'data': json.dumps(value, indent=4, cls=SafeEncoder)
                     })

        details = await get_agent_details(namespace,
                                          user,
                                          dataset,
                                          exts=supported_exts,
                                          get_task_specific_agent=get_datagpt_agent)
        if details is None:
            query_update_result(request_id, {
                'status': "failure",
                "message": f"LLM DataGPT Agent could not be found/built for {label}. Metadata and fileformats are typical issues. See agent log for why",
                "result": {}
            })
            return

        agent    = details['agent']
        metadata = details['metadata']

        # power/economy
        cascade_id = mode if mode in ['power', 'economy'] else None

        # Now run the query
        result = await run_in_threadpool(lambda: agent.query(query, cascade_id=mode))

        # => Answer is assumed to be a json
        result = json.loads(json.dumps(result, indent=4, cls=SafeEncoder))

        sample_response = """
        {
            "query": "how many rows are there?",
            "answer": "There are 6166 rows in the dataframe.",
            "thought": [
                ""
            ],
            "code": {
                "dialect": "pandas",
                "snippets": []
            }
        }
        """

        # Result
        result['metadata'] = metadata


        stats['query_success'] += 1
        stats['datasets'][label]['query_count'] += 1
        stats['datasets'][label]['query_success'] += 1
        query_update_result(request_id, {
            "status": "success",
            "result": result
        })
    except Exception as e:
        stats['query_failure'] += 1
        stats['datasets'][label]['query_count'] += 1
        stats['datasets'][label]['query_failure'] += 1
        logger.exception(f"Failed to run query",
                         extra={
                             "source": "service",
                             'request_id': request_id,
                             "user": params.get('user', "unknown"),
                             "dataset": params.get('dataset', "unknown"),
                         })
        query_update_result(request_id, {
            "status": "failure",
            "answer": f"Unable to construct the answer. Could be an internal agent error. See the agent log",
            "result": {
                "answer": str(e)
            }
        })



@app.get("/qna/status")
async def qna_status(request_id: str):
    """
    Get the status of the query request

    Parameters
    ----------
    request_id: str
                UUID generated for the request

    Returns
    -------
    status: dict
         Dictionary with request id, query, status, message and data
    """

    # First get the params
    try:

        cache = get_cache()

        if request_id not in cache:
            logger.error(f"Query Status: Invalid Request ID",
                         extra={
                             'request_id': request_id,
                             "source": "service",
                         })
            return {
                "request_id": request_id,
                "status": "failure",
                'answer': "Data not available. Either the request is invalid or the memory with that request has been cleared on restart"
            }

        value: dict = cache[request_id]
        status = value['status']
        logger.debug(f"Query Status: {status}",
                     extra={
                         "source": "service",
                         'request_id': request_id,
                         "dataset": value.get('dataset', 'unknown'),
                         "user": value.get('user', 'unknown'),
                         'data': json.dumps(value,indent=4, cls=SafeEncoder)
                     })

        return {
            "request_id": request_id,
            "query": value['query'],
            "status": value['status'],
            'message': value.get('message', ""),
            'data': value.get('result',{})
        }
    except Exception as e:
        return {
            "request_id": request_id,
            "query": value['query'],
            "status": "failure",
            "message": str(e),
            "data": {}
        }

@app.post("/qna")
async def qna(user: str,
              dataset: str,
              query: str,
              background_tasks: BackgroundTasks,
              mode: str = 'economy',
              context: str = "",
              namespace="datagpt",
              policy: dict = {},
              extra: dict = {}
):
    """
    Initiate a new request

    Parameters
    ----------
    user: str
          User (an unintepreted string)
    query: str
           A string
    namespace: str
           A namespace associated with this instance of the service. Multiple
    mode: str
           (economy|power) Power will result in use of GPT4
    context: str
           Any additional text
    policy: dict
           List of policies to enforce

    Returns
    -------
    status: dict
         Dictionary with request id, query, status, and data
    """

    cache = get_cache()
    request_id = str(uuid4())

    params = {
        "user": user,
        "dataset": dataset,
        "context": context,
        "namespace": namespace,
        "query": query,
        "policy": policy,
        "mode": mode
    }
    logger.debug(f"Building Index",
                extra={
                    "source": "service",
                    "user": user,
                    "dataset": dataset,
                    "data": json.dumps(params, indent=4, cls=SafeEncoder)
                })

    cache[request_id] = {
        'query': query,
        "status": "pending",
        "user": user,
        "dataset": dataset,
        "params": params
    }

    # Run the background task...
    background_tasks.add_task(qna_run, request_id)

    return {
        "request_id": request_id,
        "status": "pending",
        "query": query,
        "data": {}
    }

@app.on_event("startup")
def app_startup():

    t = BuildAgentThread(get_datagpt_agent)
    t.start()
    initialize_stats()
