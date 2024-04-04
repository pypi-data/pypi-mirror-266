import os
import sys
import time
import json
import copy
import traceback
import logging
from urllib.parse import urlencode

import httpx
import asyncio
from asgiref.sync import sync_to_async, async_to_sync

from enrichsdk.lib import get_credentials_by_name

logger = logging.getLogger('app')

class HedwigClient():

    def __init__(self, cred):

        if isinstance(cred, str):
            self.cred = get_credentials_by_name(cred)
        else:
            self.cred = cred

    async def access_singlestep(self,
                          request_action,
                          status_action,
                          params,
                          timeout=10):
        """
        Single blocking call to the LLM
        """

        url = self.cred['url']
        q = f"{request_action}?{urlencode(params)}"
        tries = 3
        while tries > 0:
            try:
                response = httpx.get(url + q)
                break
            except httpx.TimeoutException:
                traceback.print_exc()
                logger.exception("Timeout while accessing LLM Agent")
                await asyncio.sleep(10)
            except:
                logger.exception("Error while accessing LLM Agent")

            tries -= 1
        if tries == 0:
            response = {
                'status': 'failure',
                'message': "Unable to reach LLM to start request after retries",
                '_request': params
            }
            return response

        response = response.json()
        if 'status' not in response:
            response = {
                'status': 'failure',
                'message': "Invalid response from LLM Agent: Missing status",
                '_request': params
            }
            return response

        status = response['status']
        if status != 'pending':
            status['_request'] = params
            return response

        if 'request_id'not in response:
            response = {
                'status': 'failure',
                'message': "Invalid response from LLM Agent: Missing request id",
                '_request': params
            }
            return response

        request_id = response['request_id']
        if not isinstance(request_id, str) or len(request_id) == 0:
            response = {
                'status': 'failure',
                'message': "Invalid response from LLM Agent: Invalid request id",
                '_request': params
            }
            return response

        tries = 20
        client = httpx.AsyncClient()
        try:
            while tries > 0:

                await asyncio.sleep(5)

                q = f"{status_action}?request_id={request_id}"
                # print("Calling async client get", url + q)
                try:
                    response = await client.get(url + q)
                except httpx.ReadTimeout:
                    # print("Read timeout")
                    continue
                except httpx.TimeoutException:
                    # Happens first time with cold agent
                    # print("Timeout Exception")
                    if tries == 20: # first time
                        continue
                    else:
                        return {
                            "request_id": None,
                            "status": "failure",
                            "message": "Unable to reach after retries. Agent could be busy",
                            "_params": params
                        }

                response = response.json()
                # print(f"Try {tries}", response)
                status = response.get('status', 'failure')

                # print("Found status", status)
                # print("Returning")
                # print(json.dumps(response, indent=4))
                if status != 'pending':
                    response = response['data']
                    response['_request'] = params
                    return response

                tries -= 1
                # print("Sleeping for 5 seconds")
                await asyncio.sleep(timeout)

        except httpx.TimeoutError:
            logger.exception("Timeout while accessing LLM")
            traceback.print_exc()
        except:
            logger.exception("Error while accessing LLM")
            traceback.print_exc()
        finally:
            await client.aclose()

        # print("Returning response")
        return {
            "request_id": None,
            "status": "failure",
            "answer": "Internal error while accessing LLM Agent. See log",
            '_request': params
        }

    async def access_multistep_status(self, action, params):

        url = self.cred['url']
        q = f"{action}?{urlencode(params)}"
        request_id = params.get('request_id', None)
        try:
            if request_id is None:
                return {
                    "request_id": None,
                    "status": "failure",
                    "query": "",
                    "answer": "Invalid request to LLM Agent. Missing request_id",
                    "_request": params
                }

            print("Calling async client get", url + q)

            try:
                client = httpx.AsyncClient()
                response = await client.get(url + q)
                response = response.json()
                data = response.pop('data', {})
                response.update(data)
                response['request_id'] = request_id
                if 'answer' not in response:
                    response['answer'] = "No answer received"
                if 'query' not in response:
                    if 'question' in response:
                        response['query'] = response['question']
                    else:
                        response['query'] = ''

                return response
            except:
                logger.exception("Error while accessing LLM")
                traceback.print_exc()
                return {
                    "request_id": request_id,
                    "status": "pending",
                    "query": "",
                    "answer": "Unable to reach LLM Agent",
                    "_request": params
                }
            finally:
                await client.aclose()
        except:
            logger.exception("Unable to reach LLM Agent. See log")
            return {
                "request_id": None,
                "status": "failure",
                "query": "",
                "answer": "Internal error while accessing LLM Agent. See log",
                "_request": params
            }

    async def access_multistep_initiate(self, action, params):


        url = self.cred['url']
        q = f"{action}?{urlencode(params)}"

        # => Handle the cold-start when the document is loading and the agent is blocked...
        tries = 3
        while tries > 0:
            try:
                response = httpx.get(url + q)
                break
            except httpx.TimeoutException:
                await asyncio.sleep(10)
                tries -= 1

        if tries == 0:
            response = copy.copy(params)
            response.update({
                'response_id': None,
                'status': "failure",
                "answer": "Unable to reach LLM to start request after retries"
            })
        else:
            response = response.json()

        # Now we got a response...
        # print(json.dumps(response, indent=4))
        if ((response is None) or
            (not isinstance(response, dict)) or
            (len(response) == 0)):
            logger.error("Invalid response from agent",
                         extra={
                             'data': str(response)
                         })
            response = {
                'response_id': None,
                'status': "failure",
                "query": query,
                "answer": "Invalid response from LLM Agent"
            }

        status = response.get('status', None)
        answer = response.get('answer', None)
        if ((answer is None) and (status != 'pending')):
            logger.error("Received no answer",
                         extra={
                             'data': json.dumps(response, indent=4)
                         })
            answer = response['answer'] = "No answer. Possibly an internal error"

        return response


def test_hedwig_singlestep():
    client = HedwigClient('llm-default')

    response = async_to_sync(client.access_singlestep)(request_action="/qna",
                                                       status_action="/qna/status",
                                                       params={
                                                           "user": "venkata",
                                                           "dataset": "verizon",
                                                           "mode": "internal",
                                                           "query": "What is this document about?",
                                                           "namespace": "default",
                                                           "context": ""


                                                       })
    print(json.dumps(response, indent=4))

def test_hedwig_multistep():
    client = HedwigClient('llm-default')

    response = async_to_sync(client.access_multistep_initiate)("/qna",
                                                               params={
                                                                   "user": "venkata",
                                                                   "dataset": "verizon",
                                                                   "mode": "internal",
                                                                   "query": "What is this document about?",
                                                                   "namespace": "default",
                                                                   "context": ""
                                                       })
    print(json.dumps(response, indent=4))

    request_id = response['request_id']

    tries = 20
    while tries > 0:
        time.sleep(5)
        response = async_to_sync(client.access_multistep_status)("/qna/status",
                                                               params={
                                                                   "request_id": request_id
                                                               })
        print(json.dumps(response, indent=4))
        status = response.get('status', None)
        if status == 'pending':
            tries -= 1
            continue
        else:
            break

if __name__ == "__main__":

    #test_hedwig_singlestep()
    test_hedwig_multistep()
