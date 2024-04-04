import json
import time
import string
from re import sub

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback

from . import agent_events
from llmsdk.lib import SafeEncoder
from llmsdk.services.log import *

__all__ = ['LLMDataExplainer']


class LLMDataExplainer(object):
    """
    A generic bot to convert JSON objects into descriptive text
    """

    def __init__(self,
                 name,
                 cred={},
                 platform="openai"):
        """
        init the bot
        name: name of the bot
        cred: credentials object
        platform: name of the platform backend to use
                default to openai platform for now
                will be extended in the future to suuport other platforms
        """

        start_time = time.time()

        # logging
        self.logger = get_logger()

        # defaults
        self.metadata = {}
        self.max_llm_tokens = 1024

        # name
        self.agent_name = name
        self.agent_type = "data-explainer"

        # creds
        self.cred = cred
        # LLM params
        self.platform = platform

        # init the llm and embeddings objects
        self.llm = self._get_llm_objs(platform=self.platform,
                                      cred=self.cred)

        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "platform": self.platform,
            },
            "events": []
        }
        # log that the agent is ready
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_READY, duration)

    ## helper functions

    def _create_id(self, string):
        """
        create a unique identifier from a string
        """
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def _log_event(self, event_name, duration=0, params={}):
        """
        format an event object to store in the agent's metadata
        event_name: name of the event to log
        duration: how long did this event take, only needed for events
                   that require some waiting (e.g. RTT to LLM APIs)
        params: any other info needed to be logged
        """

        ts = time.time() - duration # to get the actual start time
        event_id = self._create_id(f'{event_name}-{ts}')

        event = {
            "id": event_id,
            "agent": self.agent_name,
            "agent_type": self.agent_type,
            "timestamp": round(ts, 3),
            "duration": round(duration, 3),
            "name": event_name,
            "params": params,
        }
        self.metadata['events'].append(event)

        return event

    def _get_llm_objs(self, platform, cred):
        # get the api key from creds
        api_key = self._get_api_key(cred, platform)

        # init the model
        if platform == "openai":
            # get the llm object
            llm = ChatOpenAI(temperature=0,
                             openai_api_key=api_key,
                             model="gpt-3.5-turbo",
                             max_tokens=self.max_llm_tokens,
                             request_timeout=60)
        else:
            llm = None

        return llm

    def _get_api_key(self, cred, key):
        """
        get the API key from the cred
        """
        api_key = None
        if isinstance(cred, str):
            api_key = cred
        if isinstance(cred, dict) and key in cred:
            api_key = cred[key]
        return api_key

    def _err_msg(self, t):
        msgs = {
            "field": "I'm having trouble understanding. Try another way of wording your query."
        }
        return msgs.get(t, "Something went wrong, try your query again.")

    ## interfaces

    def get_metadata(self):
        """
        return metadata collected by the agent
        """
        return self.metadata

    def get_prompt(self, json_obj, instructions, common=""):
        """
        generate a prompt for querying the LLM
        """
        # construct the prompt template
        sys_msg = """You are a highly advanced, AI-enabled, JSON to TEXT converter.
        You will be given a json object and a set of instructions. Use the instructions to generate text from the json object.
        """

        human_msg = f"""Here is the json object:
        ------ BEGIN JSON OBJECT ------
        {json_obj}
        ------- END JSON OBJECT -------

        Here are the instructions:
        ------ BEGIN INSTRUCTIONS ------
        {common}
        {instructions}
        ------- END INSTRUCTIONS -------"""

        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=human_msg),
        ]

        return messages

    def generate_text(self, json_obj, instructions, common):
        """
        run a prompt against the LLM using the policy spec
        """
        success = True
        response = None
        stats = {}

        # construct the prompt to the policy bot
        prompt = self.get_prompt(json_obj, instructions, common)

        # run the query
        try:
            if self.platform in ['openai', 'azure']:
                with get_openai_callback() as cb:
                    response = self.llm(prompt)
                    response = response.content
                stats = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost": round(cb.total_cost, 4)
                }
        except:
            success = False

        # run the query against the similar docs
        result = {
            "text": response,
        }

        return success, result

    def json_to_text(self, json_obj, policy):
        """
        run the agent on the json object and a policy spec
        """
        start_time = time.time()

        spec = policy.get("instructions", {})
        sep = spec.get("sep", "|")

        # for each key
        text_obj = {}
        for insight_key, item in json_obj.items():
            # check if we have a prompt spec defined to generate the text
            prompt_key = insight_key.split(sep)[0]

            common = spec.get("__common__", "")
            prompt_spec = spec.get("keys", {}).get(prompt_key)
            if not prompt_spec:
                self.logger.debug(f"No prompt defined for [{prompt_key}], skipping",
                             extra={
                                 'source': self.agent_name
                             })
                continue

            # we have a prompt spec, use it to generate the text
            success, result = self.generate_text(item, prompt_spec, common)

            if success:
                text_obj[insight_key] = result
            else:
                self.logger.debug(f"Something went wrong generating text for [{insight_key}]",
                             extra={
                                 'source': self.agent_name,
                                 'data': json.dumps(item, indent=4)
                             })

            # log the event
            params = {
                "result": result,
                "policy": policy,
            }
            duration = time.time() - start_time
            event = self._log_event(agent_events._EVNT_DOCGEN, duration, params=params)

        return text_obj
        

################### BEGIN TESTBED ###################

if __name__ == "__main__":

    # init the explainer bot
    survey_bot = LLMDataExplainer(name="niel-son",
                                  platform="openai")
