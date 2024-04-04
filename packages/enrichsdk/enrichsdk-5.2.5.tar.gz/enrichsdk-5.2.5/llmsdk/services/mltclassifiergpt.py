from uuid import uuid4

from fastapi.concurrency import run_in_threadpool

from .basegpt import BaseGPT
from .lib import *
from ..agents import LLMMultiLabelTextClassifier

logger = get_logger()


class MultiClassifierGPT(BaseGPT):

    def __init__(self):
        super().__init__()
        self.name = "MultiClassifierGPT"
        self.agentname = "multiclassifiergpt"
        self.platform = "openai"
        self.namespace = "multiclassifiergpt"

    async def get_llm_agent(self):
        agentname = "multiclassifiergpt"
        platform = "openai"
        survey_agent = LLMMultiLabelTextClassifier(name=agentname, platform=platform)

        logger.debug(f"Built agent for {agentname} and platform {platform}")

        return {
            "agent": survey_agent
        }

    async def qna_run(self, request_id):
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

            # Now run the query
            success, result = await run_in_threadpool(
                lambda: self.agent.label(query, label_spec=self.get_customer_profile_spec()))

            if success:
                json_result = json.loads(json.dumps(result, indent=4, cls=SafeEncoder))

                stats['query_success'] += 1
                stats['datasets'][label]['query_count'] += 1
                stats['datasets'][label]['query_success'] += 1
                query_update_result(request_id, {
                    "status": "success",
                    "result": json_result
                })
            else:
                stats['query_failure'] += 1
                stats['datasets'][label]['query_count'] += 1
                stats['datasets'][label]['query_failure'] += 1
                query_update_result(request_id, {
                    "status": "failure",
                    "result": 'Error'
                })
                logger.exception(f"Failed to run query",
                                 extra={
                                     "source": "service",
                                     'request_id': request_id,
                                     "user": params.get('user', "unknown"),
                                     "dataset": params.get('dataset', "unknown"),
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

    def get_customer_profile_spec(self):
        default = {

            "persona": """You are a highly advanced, AI-enabled bot whose job is to take a question from a user and assign two labels to it.
    The first label is what kind of insight is being asked about.
    The second label is what kind of cohort is being asked about.""",

            "instructions": """The questions will be about the results of a survey across multiple respondent cohorts for multiple products.
    Note that sometimes a question can be about all the products in the survey without asking about population cohorts, and sometimes cohort information will be asked.
    The three types of population cohorts are: region, gender, age
    
    The following are metrics that could be mentioned in the question:
      - 'reach' a.k.a. 'line insights' a.k.a. 'le'
      - 'voc' a.k.a. 'sentiment score' a.k.a. 'ss'
    
    Here are the rules by which you must perform the insight label assignment:
      - If the question is asking about actionable insights, then assign insight=actionable_insights
      - If the question is asking specifically about best performing or worst performing products, then assign insight=actionable_insights
      - If the question is asking about product metrics with a specific cohort, then assign insight=le_insights
      - If the question is asking about the affinity of a population cohort to products, then assign insight=ss_insights
      - If the question is asking about product features, then assign insight=features_insights
      - If the question is asking about the audience, then assign insight=audience_insights
    
    And here are the rules by which you must perform the cohort label assignment:
      - If the question is asking about groups of respondents, then assign cohort=audience
      - If the question is asking about locations, then assign cohort=region
      - If the question is asking about gender, then assign cohort=gender
      - If the question is asking about age, then assign cohort=age
      - If the question is asking about best, or winners, or hits then assign cohort=best
      - If the question is asking about worst or losers then assign cohort=worst
      - If the question is asking about not liking something, then assign cohort=dislikes
      - If the question is asking about one metric being high and another being low, then assign cohort=mixed""",

            "synonymns": {
                "actionable insights": [
                    "survey summary",
                    "global summary",
                    "overall performance"
                ],
                "line efficiency": [
                    "le",
                    "reach",
                    "cannibalization",
                    "incremental reach",
                    "cumulative reach",
                ],
                "sentiment score": [
                    "ss",
                    "voc",
                    "voice of consumer",
                    "sentiment graph",
                    "consumer graph",
                    "consumer appetite",
                    "consumer sentiment",
                ],
            },

            "output_format": {
                "type": "json",
                "sample": '{"insight": insight, "cohort": cohort}'
            }
        }

        return default


app = FastAPI()

##############################################
# Common
##############################################
add_show_cache(app)
add_show_health(app)
policyspec = []
add_policy(app, policyspec)
multClassifierGpt = MultiClassifierGPT()
app.include_router(multClassifierGpt.router)
