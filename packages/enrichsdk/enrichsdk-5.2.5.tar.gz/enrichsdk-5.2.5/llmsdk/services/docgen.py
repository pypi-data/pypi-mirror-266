"""

This module implements the DocGen microservice. Its purpose is to wrap
around the DocGen agent and provide an integration point from end applications.
The DocGen module enables users to generate long-form documents based on a set of input documents and a spec.

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

from llmsdk.agents.docgen import LLMDocGenerator
from llmsdk.lib import SafeEncoder

from .log import *
from .lib import *

# Override default uvicorn logger...
logging.config.dictConfig(log_config)
logger = get_logger()

supported_exts=['txt', 'htm', 'html', 'pdf', 'docx', 'doc']

app = FastAPI()

# Insert policy
policyspec = []
add_policy(app, policyspec)

async def get_docgen_agent(namespace, username, dataset,
                           fullpath, files,
                           metadata,
                           drop_index=False):

    return await get_generic_agent(LLMDocGenerator,
                                   dataset,
                                   fullpath,
                                   files,
                                   metadata,
                                   drop_index=False)

add_show_cache(app)
add_show_health(app)
add_check_index(app, "docgen")
add_build_index(app, "docgen", supported_exts)

async def generate_run(request_id):
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
        profilespec = params['profilespec']
        context = params['context']
        namespace = params['namespace']
        exts = params['exts']

        stats['query_count'] += 1

        label = f"{user}_{dataset}"

        logger.debug(f"{label}: Getting agent",
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
                                          exts=exts,
                                          get_task_specific_agent=get_docgen_agent)
        if details is None:
            query_update_result(request_id, {
                'status': "failure",
                "message": f"LLM Docgen Agent not found for {label}. See agent log",
                "result": {}
            })
            return

        agent    = details['agent']
        metadata = details['metadata']

        answer   = await run_in_threadpool(lambda: agent.generate_doc(profilespec))
        result = {
            'request_id': request_id,
            "answer": answer,
            "metadata": metadata
        }
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
            "answer": f"Unable to construct the answer. Internal error. See the agent log",
            "result": {
                "answer": str(e)
            }
        })



@app.get("/generate/status")
async def generate_status(request_id: str):
    """
    Get the status of the query request

    Parameters
    ----------
    request_id: str
                UUID generated for the request

    Returns
    -------
    status: dict
         Dictionary with request id, status, message and data
    """
    # First get the params
    try:

        value: dict = {}

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

        value = cache[request_id]
        status = value.get('status', 'unknown')
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
            "status": value['status'],
            'message': value.get('message', ""),
            'data': value.get('result',{})
        }
    except Exception as e:
        logger.exception("Query Status: failure",
                     extra={
                         "source": "service",
                         'request_id': request_id,
                         "user": value.get('user',"unknown"),
                         "dataset": value.get('dataset',"unknown"),
                     })
        return {
            "request_id": request_id,
            "status": "failure",
            "message": str(e),
            "data": {}
        }

@app.post("/generate")
async def generate(user: str,
                   dataset: str,
                   profilespec: dict,
                   background_tasks: BackgroundTasks,
                   context: str = "",
                   namespace="docgen",
                   policy: dict = {},
                   extra: dict = {}
):
    """
    Initiate a new request

    Parameters
    ----------
    user: str
          User (an unintepreted string)
    profilespec: dict
           Dictionary specifying the document to the generated
    namespace: str
           A namespace associated with this instance of the service. Multiple
    context: str
           Any additional text
    policy: dict
           List of policies to enforce
    extra: dict
           Pass any other information

    Returns
    -------
    status: dict
         Dictionary with request id, query, status, and answer

    """
    cache = get_cache()

    request_id = str(uuid4())

    label = f"{user}_{dataset}"
    taskdetails = get_buildtask_details(label)
    if taskdetails is None:
        logger.error(f"Index not built yet",
                     extra={
                         'request_id': request_id,
                         "source": "service",
                         "user": user,
                         "dataset": dataset
                     })
        return {
            "request_id": request_id,
            "status": "failure",
            "answer": "Index has not been constructed yet. Please trigger a build action"
        }

    params = {
        "user": user,
        "dataset": dataset,
        "context": context,
        "namespace": namespace,
        "exts": supported_exts,
        "profilespec": profilespec,
        "policy": policy
    }
    logger.debug(f"Building index for {label}",
                extra={
                    "source": "service",
                    "user": user,
                    "dataset": dataset,
                    "data": json.dumps(params, indent=4, cls=SafeEncoder)
                })

    exists = await check_agent_details(user, dataset)
    if not exists:
        logger.error(f"Index not been built yet",
                     extra={
                         "source": "service",
                         "user": user,
                         "dataset": dataset,
                     })
        return {
            "request_id": request_id,
            "status": "failure",
            "answer": "Index has not been constructed yet. Please trigger a build action or wait if pending"
        }

    cache[request_id] = {
        "status": "pending",
        "user": user,
        "dataset": dataset,
        "params": params
    }

    # Run the background task...
    background_tasks.add_task(generate_run, request_id)

    return {
        "request_id": request_id,
        "status": "pending",
        "data": {}
    }

@app.on_event("startup")
def app_startup():

    t = BuildAgentThread(get_docgen_agent)
    t.start()
    initialize_stats()
