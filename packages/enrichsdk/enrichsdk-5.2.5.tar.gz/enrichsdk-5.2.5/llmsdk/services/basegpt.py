import json
import os
from collections import defaultdict
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter
from starlette.background import BackgroundTasks
from starlette.concurrency import run_in_threadpool

from llmsdk.lib import SafeEncoder
from llmsdk.services.lib import get_cache, initialize_stats, query_update_result, stats
from llmsdk.services.log import get_logger

logger = get_logger()


class BaseGPT():
    def __init__(self):
        """
        Base GPT services class for rolling out the microservices. Provides common routing methods

        """
        initialize_stats()
        self.name = "BaseGPT"
        self.agentname = "basegptname"
        self.platform = "openai"
        self.namespace = "basegpt"

        self.run_dir = stats.get('run_dir', self.agentname)
        self.index_name = "acme_gpt_index"
        self.persist_directory = os.path.join(self.run_dir, "index")
        self.agent = None

        self.router = APIRouter()
        self.router.add_api_route("/up", self.up, methods=["GET"])
        self.router.add_api_route("/health", self.health, methods=["GET"])
        self.router.add_api_route("/cache", self.cache_health, methods=["GET"])
        self.router.add_api_route("/qna/status", self.qna_status, methods=["GET"])
        self.router.add_api_route("/qna", self.qna, methods=["POST"])
        self.router.add_event_handler("startup", self.app_startup)

    def up(self) -> str:
        """
        Checks if service is running
        :return: Service status
        """
        return f"Service {self.agentname} is working!"

    def health(self) -> dict:
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

    def cache_health(self):
        """
        Summarize the content of the cache
        """

        cache = get_cache()
        summary = defaultdict(int)
        for k, v in cache.items():
            summary[v['status']] += 1

        return summary

    def get_customer_profile_spec(self) -> dict:
        """
        Profile spec for each customer to be used
        :return:
        """
        pass

    async def get_llm_agent(self) -> dict:
        """
        Get the LLM agent configuration class
        :return: agent configuration
        """
        pass

    def startup_extra_steps(self):
        """
        Run additional startup steps when app is initiated
        :return:
        """
        pass

    async def qna_run_execute(self, query):
        """
        Perform operation using agent, override for different type of operation
        :param query: Query to be searched
        :return:
        """
        spec = self.get_customer_profile_spec()
        return await run_in_threadpool(lambda: self.agent.query(query, spec))

    async def qna_run(self, request_id):
        """
        Execute query against the agend
        :param request_id: Request ID of the request
        :return:
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

            params = value['params']
            user = params['user']
            dataset = params['dataset']
            query = params['query']

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

            stats['datasets'][label] = {
                'loaded': datetime.now().replace(microsecond=0).isoformat(),
                'username': user,
                'agent_created': True,
                'agent_status': "Created",
                "query_count": 0,
                "query_success": 0,
                "query_failure": 0,
            }

            spec = self.get_customer_profile_spec()

            # Now run the query
            result = await self.qna_run_execute(query)

            if result.get("success"):
                key = result.get("key")
                logger.debug(f"Query: {query}\nKEY: {key}\n")
                json_result = json.loads(json.dumps(result, indent=4, cls=SafeEncoder))

                stats['query_success'] += 1
                stats['datasets'][label]['query_count'] += 1
                stats['datasets'][label]['query_success'] += 1
                query_update_result(request_id, {
                    "status": "success",
                    "result": json_result,
                })
            else:
                suggestions = result.get("suggestions")
                logger.debug(f"Query: {query}\nSuggestions: {suggestions}\n")
                json_result = json.loads(json.dumps(result, indent=4, cls=SafeEncoder))
                stats['datasets'][label]['query_count'] += 1
                stats['datasets'][label]['query_failure'] += 1
                query_update_result(request_id, {
                    "status": "success",
                    "result": json_result,
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
                    "text": str(e)
                }
            })

    async def qna_status(self, request_id: str):
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
                             'data': json.dumps(value, indent=4, cls=SafeEncoder)
                         })

            return {
                "request_id": request_id,
                "query": value['query'],
                "status": value['status'],
                'message': value.get('message', ""),
                'data': value.get('result', {})
            }
        except Exception as e:
            return {
                "request_id": request_id,
                "query": request_id,
                "status": "failure",
                "message": str(e),
                "data": {}
            }

    async def qna(self, user: str,
                  query: str,
                  dataset: str,
                  background_tasks: BackgroundTasks,
                  mode: str = 'economy',
                  context: str = "",
                  policy: dict = {},
                  extra: dict = {}
                  ):

        """
        Run the query against the LLM microservices

        :param user: User
        :param query:  Query
        :param dataset: Dataset
        :param background_tasks:
        :param mode: Type of mode
        :param context:
        :param policy:
        :param extra:
        :return:
        """
        cache = get_cache()
        request_id = str(uuid4())

        params = {
            "user": user,
            "dataset": dataset,
            "context": context,
            "namespace": self.namespace,
            "query": query,
            "policy": policy,
            "mode": mode
        }

        cache[request_id] = {
            'query': query,
            "status": "pending",
            "user": user,
            "dataset": dataset,
            "params": params
        }

        # Run the background task...
        background_tasks.add_task(self.qna_run, request_id)

        return {
            "request_id": request_id,
            "status": "pending",
            "query": query,
            "data": {}
        }

    async def app_startup(self):
        """
        Start the LLM microservices
        :return:
        """
        logger.info("Starting agent [" + self.agentname + "] with namespace [" + self.namespace + "]...")
        if self.agent is None:
            details = await self.get_llm_agent()
            if details is None:
                query_update_result("request_id", {
                    'status': "failure",
                    "message": f"LLM QueryMapper Agent could not be found/built",
                    "result": {}
                })
                return

            self.agent = details['agent']

        self.startup_extra_steps()
