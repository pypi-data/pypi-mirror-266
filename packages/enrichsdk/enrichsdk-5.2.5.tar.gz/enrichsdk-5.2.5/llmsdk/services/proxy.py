"""
Simple LLM Proxy that works with the front end. This derives from the QnA service module.

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
from logging.config import dictConfig
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi_utils.tasks import repeat_every

from llmsdk.lib import SafeEncoder
from litellm import completion

from .log import *
from .lib import *

# Override default uvicorn logger...
logging.config.dictConfig(log_config)
logger = get_logger()

app = FastAPI()

# Insert policy
policyspec = []
add_policy(app, policyspec)

"""
Samples responses of llmlite 

        sample_response = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": "I'm sorry, but I don't have the capability to provide real-time weather information. However, you can easily check the weather in San Francisco by searching online or using a weather app on your phone.",
                    "role": "assistant"
                    }
                }
            ],
            "created": 1691790381,
            "id": "chatcmpl-7mUFZlOEgdohHRDx2UpYPRTejirzb",
            "model": "gpt-3.5-turbo-0613",
            "object": "chat.completion",
            "usage": {
                "completion_tokens": 41,
                "prompt_tokens": 16,
                "total_tokens": 57
            }
        }
"""

class ProxyAgent():

    def completion(self, request_id, params):

        mode = params.get("mode", "gpt-3.5-turbo")
        model = "gpt-3.5-turbo" if mode == "normal" else "gpt-4"

        query = params['query']

        completion_params = { 
            "model": model,
            "messages": [
                {
                    "content": query,
                    "role": "user"
                }
            ]
        }

        try:
            response = completion(**completion_params)
            logger.debug(f"Response from server",
                             extra={
                                 "source": "service",
                                 'request_id': request_id,
                                 "user": params.get('user', "unknown"),
                                 "dataset": params.get('dataset', "unknown"),
                                 'data': json.dumps(response, indent=4, cls=SafeEncoder)
                             })
            final_response = {
                "status": response.get('status', 'success'),
                "query": query,
                "answer": response['choices'][0]['message']['content'],
                'metadata': response
            }
            
        except Exception as e:
            logger.exception(f"Failure during execution",
                             extra={
                                 "source": "service",
                                 'request_id': request_id,
                                 "user": params.get('user', "unknown"),
                                 "dataset": params.get('dataset', "unknown"),
                         })
            final_response = {
                "status": "failure",
                "query": query,                
                "answer": "Error while accessing the LLM backend"
            }        
    
        return final_response

proxy = ProxyAgent()

@app.get("/cache")
def cache_health():
    """
    Summarize the content of the cache
    """

    cache = get_cache()
    summary = defaultdict(int)
    for k, v in cache.items():
        summary[v['status']] += 1

    return summary

@app.get("/health")
def health():
    """
    Return usage statistics

    Returns
    -------
    stats: dict
           Usage statistics

    """
    logger.info("Returning stats",
                extra={
                    'data': json.dumps(stats, indent=4)
                })
    return stats


def query_update_result(request_id, result):

    # First get the params
    cache = get_cache()
    value = cache[request_id]

    for k, v in result.items():
        value[k] = result[k]

    status = result.get('status', 'unknown')
    logger.debug(f"Result: {status}",
                extra={
                    "request_id": request_id,
                    "source": "service",
                    "user": value.get("user", "unknown"),
                    "dataset": value.get("dataset", "unknown"),
                    'data': json.dumps(result, indent=4, cls=SafeEncoder)
                })

async def query_run(request_id):
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
        query   = params['query']
        namespace = params['namespace']
        label = f"{user}_{dataset}"

        logger.debug(f"{label}: Running Query",
                     extra={
                         "source": "service",
                         "user": user,
                         "dataset": dataset,
                         "request_id": request_id,
                         'data': json.dumps(value, indent=4, cls=SafeEncoder)
                     })

        stats['query_count'] += 1


        result   = await run_in_threadpool(lambda: proxy.completion(request_id, params))
        result['request_id'] = request_id

        logger.debug(f"Raw result received",
                     extra={
                         "source": "service",
                         "request_id": request_id,
                         "user": user,
                         "dataset": dataset,
                         "data": json.dumps(result, indent=4, cls=SafeEncoder)
                     })
        result['answer'] = result['answer'].strip()
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
            "message":  f"Unable to construct the answer. Internal error. See the agent log",
            "result": {
                "question": query,
                "answer": "Error while accessing the LLM Agent. See log",
                "raw": [
                    str(e)
                ]
            }
        })



@app.get("/qna/status")
async def query_status(request_id: str):
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
                "message": "Request ID not found"
            }

        value = cache[request_id]
        status = value['status']
        response = {
            "request_id": request_id,
            "status": value['status'],
            'message': value.get('message', ""),
            'data': value.get('result',{})
        }
        logger.debug(f"Query Status: {status}",
                     extra={
                         "source": "service",
                         'request_id': request_id,
                         "dataset": value.get('dataset', 'unknown'),
                         "user": value.get('user', 'unknown'),
                         'data': json.dumps(response,indent=4, cls=SafeEncoder)
                     })
        return response

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

@app.post("/qna")
async def query_index(user: str,
                      dataset: str,
                      query: str,
                      background_tasks: BackgroundTasks,
                      mode: str = 'internal',
                      context: str = "",
                      namespace="default",
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
    context: str
           Any additional text
    policy: dict
           List of policies to enforce
    extra: dict
           Pass any other information

    Returns
    -------
    status: dict
         Dictionary with request id, query, status and data
    """

    cache = get_cache()
    request_id = str(uuid4())

    params = {
        "user": user,
        "dataset": dataset,
        "query": query,
        "mode": mode,
        "context": context,
        "namespace": namespace,
        "policy": policy
    }
    label = f"{user}_{dataset}"

    if label not in stats['datasets']:
        stats['datasets'][label] = {
            "query_count": 0,
            "query_success": 0,
            "query_failure": 0,
        }
        
    
    logger.debug(f"Starting query",
                extra={
                    "source": "service",
                    "user": user,
                    "dataset": dataset,
                    "data": json.dumps(params, indent=4, cls=SafeEncoder)
                })

    cache[request_id] = {
        "status": "pending",
        "user": user,
        "dataset": dataset,
        "query": query,        
        "params": params
    }

    # Run the background task...
    background_tasks.add_task(query_run, request_id)

    return {
        "request_id": request_id,
        "status": "pending",
        "data": {}
    }

@app.on_event("startup")
def app_startup():

    initialize_stats()
