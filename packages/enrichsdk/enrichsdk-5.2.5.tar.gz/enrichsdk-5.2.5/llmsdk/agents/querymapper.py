import time
import json
import string

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback

from llmsdk.agents.basellm import BaseLLMAgent

from . import agent_events
from llmsdk.lib import SafeEncoder
from llmsdk.services.log import *

__all__ = ['LLMQueryMapper']


class LLMQueryMapper(BaseLLMAgent):
    """
    Class to do querying of a set of strings to return the closest matching string to the query
    """

    def __init__(self,
                 name,
                 cred={},
                 platform="openai",
                 statestore="redis",
                 topk=5):
        """
        init the LLM query agent
        name: name of the agent
        cred: credentials object
        platform: name of the LLM platform backend to use
                default to OpenAI GPT platform for now, Azure is also supported
                will be extended in the future to suuport other models
        memory_size: how many tokens of memory to use when chatting with the LLM
        """

        start_time = time.time()

        # init the base class
        super().__init__(name=name,
                         cred=cred,
                         platform=platform,
                         agent_type="querymapper",
                         statestore=statestore)

        # defaults
        self.chunk_size = 1000
        self.chunk_overlap = 300
        self.index = None
        self.metadata = {}
        self.vdb_client = None
        self.index_name = None
        self.index_store = None
        self.topk = topk
        self.doc_signatures = []
        self.docs = {}

        # LLM params
        self.platform = platform
        self.chaintype = "stuff"

        # init the llm and embeddings objects
        self.llm, self.embeddings = self._get_llm_objs(platform=self.platform,
                                                       cred=self.cred)

        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "type": self.agent_type,
                "platform": self.platform,
                "chaintype": self.chaintype,
            },
            "events": []
        }
        # log that the agent is ready
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_READY, duration)

    ## helper functions

    def _get_query_prompt_ranking(self, query, docs, spec):
        """
        generate a prompt for running a query to find the most relevant doc from a set
        """
        # how many docs to choose between
        num_choices = len(docs)

        # construct the choices
        choices = []
        for d in docs:
            choice = f"TEXT: {d.page_content}" + "\n"
            choice += f"ID: {d.metadata['id']}" + "\n"
            choice += f"SCORE: {1-d.metadata['distance']}"
            choices.append(choice)
        choices = "\n\n".join(choices)

        # define output format
        output_format = "Respond with a json dictionary as follows: " + "\n"
        output_format += '{"is_similar": is_similar, id": ID}'

        # construct the context
        context = spec.get("context", [])
        context = [f'- {c}' for c in context]
        context = "\n".join(context)

        # construct the prompt
        sys_msg = f"""You are a highly advanced AI-enabled semantic text matching program.

You will be presented with a user's query and a set of {num_choices} possible matching text chunks.
The text chunks will be presented as successive sets of:
TEXT: text_chunk
ID: identifier
SCORE: relevance_score

You task is to respond with two pieces of information: 'is_similar' and 'id'

First, determine whether the query is similar to any of the text chunks.
If the query is similar, then set 'is_similar' to true else set it to false

Second, determine the ID of the MOST RELEVANT text chunk that matches the query.
Use your judgement, the text chunk with the highest SCORE may or may not always be the most relevant match.

{output_format}

Keep the following context in mind while performing your task:
{context}
"""
        human_msg = f"""
------ BEGIN QUERY ------
{query}
------ END QUERY ------

------ BEGIN TEXT CHUNKS ------
{choices}
------ END TEXT CHUNKS ------

Response:"""

        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=human_msg),
        ]

        return messages

    def _get_query_prompt_intent(self, query, answer, spec):
        """
        generate a prompt for extracting intent params from a query template
        """

        metadata = answer.get("selection", {}).get("metadata", {})

        # get intent variables
        key = metadata.get("key", "")
        intents = key.split('|')[1:]
        intents = list(set(intents))
        intents_str = [f'- {i}' for i in intents]
        intents_str = "\n".join(intents_str)

        # get the context
        context = spec.get("context", [])
        context = [f'- {c}' for c in context]
        context = "\n".join(context)

        # get the rules
        rules = json.loads(metadata.get("rules", json.dumps([])))
        rules = [f'- {r}' for r in rules]
        rules = "\n".join(rules)

        # define output format
        op = [f'"{i}": value' for i in intents]
        output_format = "{" + ", ".join(op) + "}"

        # construct the prompt
        sys_msg = f"""You are a highly advanced AI-enabled intent detection program.

You will be presented with a user's query and a set of intent variables to identify from the query.
The intent variables are:
{intents_str}

Your task is to extract the value of each intent variable from the query and respond.

Respond with ONLY the intent key and values in a json dictionary as follows:
{output_format}

Keep the following context in mind while performing your task:
{context}
{rules}
"""
        human_msg = f"""
------ BEGIN QUERY ------
{query}
------ END QUERY ------

Response:"""

        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=human_msg),
        ]

        return messages


    ##
    ## interfaces
    ##

    def run_query_ranking(self, query, spec):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # get the similar docs
        docs = self.get_similar_docs(query, topk=self.topk)
        sources = [{"id": d.metadata.get('id'), "content": d.page_content, "metadata": d.metadata, "distance": d.metadata.get('distance')} for d in docs]

        # construct the prompt
        prompt = self._get_query_prompt_ranking(query, docs, spec)

        # call the LLM
        response = self.llm(prompt)

        # construct result
        is_relevant = False
        suggestions = []
        try:
            answer = json.loads(response.content)
            _id = answer.get("id")
            # we refer to this as relvance from here on
            is_relevant = answer.get("is_similar")
            if is_relevant:
                for s in sources:
                    if _id == s.get("metadata", {}).get("id"):
                        answer["selection"] = s
                        break
        except:
            pass

        if is_relevant and "selection" not in answer:
            # we are defaulting to the most relevant match according to semantic search
            answer["selection"] = sources[0]
            answer["id"] = sources[0].get("id")
            suggestions = [d.page_content for d in docs]

        if not is_relevant:
            suggestions = [d.page_content for d in docs]

        # run the query against the similar docs
        result = {
            "success": True,
            "is_relevant": is_relevant,
            "question": query,
            "answer": answer,
            "suggestions": suggestions,
            "sources": sources,
        }

        return result

    def run_query_intent(self, query, answer, spec):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # construct the prompt
        prompt = self._get_query_prompt_intent(query, answer, spec)

        # call the LLM
        response = self.llm(prompt)

        # construct result
        try:
            answer = json.loads(response.content)
            success = True
        except:
            success = False

        # run the query against the similar docs
        result = {
            "success": success,
            "question": query,
            "answer": answer,
        }

        return result

    def query(self, query, spec):
        """
        run a query on an index using an llm chain object
        query: query string
        """

        start_time = time.time()

        # first, get the top-ranked query template
        # run the ranking query
        try:
            if self.platform in ['openai', 'azure']:
                with get_openai_callback() as cb:
                    result_ranking = self.run_query_ranking(query, spec)
                stats = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost": round(cb.total_cost, 4)
                }
            else:
                result_ranking = self.run_query_ranking(query, spec)
                stats = {}
        except:
            result_ranking = {
                "success": False,
                "question": query,
                "answer": self._err_msg('field'),
                "sources": [],
            }
            stats = {}

        # log the event
        params = {
            "query": query,
            "mode": "ranking",
            "result": result_ranking.copy() if result_ranking is not None else None,
            "stats": stats,
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

        # for the final return
        result = result_ranking

        # then, parse the query template to get the widget key
        if result_ranking.get("success") and result_ranking.get("is_relevant"):
            # start timing again
            start_time_intent = time.time()

            # run the extraction query
            ranking_answer = result_ranking.get("answer", {})
            try:
                if self.platform in ['openai', 'azure']:
                    with get_openai_callback() as cb:
                        result_intent = self.run_query_intent(query, ranking_answer, spec)
                    stats = {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_cost": round(cb.total_cost, 4)
                    }
                else:
                    result_intent = self.run_query_intent(query, ranking_answer, spec)
                    stats = {}
            except:
                result_intent = {
                    "success": False,
                    "question": query,
                    "answer": self._err_msg('field'),
                    "sources": [],
                }
                stats = {}

            # construct the key
            if result_intent['success']:
                intent_answer = result_intent.pop("answer", {})
                key = ranking_answer.get("selection", {}).get("metadata", {}).get("key", "")
                for intent, value in intent_answer.items():
                    if value:
                        key = key.replace(intent, value)
                result_intent["key"] = key

            # log the event
            params = {
                "query": query,
                "mode": "intent",
                "result": result_intent.copy() if result is not None else None,
                "stats": stats,
            }
            duration = time.time() - start_time_intent
            event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

            # for the final return
            result = result_intent
        else:
            result.pop("answer")
            result.pop("sources")

        # add the event to the result
        result['metadata'] = {
            "timestamp": event['timestamp'],
            "duration": time.time() - start_time,
        }

        return result

    def load_spec(self, spec, persist_directory, index_name):
        """
        load up the spec with templates for the agent to refer to
        """

        # make note of the topk relevant expected results
        topk = spec.get("topk", 5)
        context = spec.get("context", [])

        # load the data
        templates = spec.get("templates", [])
        for doc in templates:
            # one search doc at a time
            template = doc.get("template")
            if not template:
                continue

            # add the rules to the metadata
            metadata = doc.get("metadata", {})
            if "rules" in metadata:
                metadata["rules"] = json.dumps(metadata["rules"])

            data = self.load_data(content=template,
                                   source="str",
                                   metadata=metadata)
            if not self.index:
                self.create_add_index(data=data,
                                       store="chroma",
                                       persist_directory=persist_directory,
                                       index_name=index_name)
            else:
                self.add_to_index(data=data)

        # set the topk value for the agent
        # this is done here to handle a peculiarity with the LLMBase class
        self.topk = topk


## TESTBED ##

if __name__ == "__main__":

    def get_profilespec():

        # ruleset
        RULE__TIME_PERIOD = "TIME_PERIOD must be one of 'day', 'week', 'month', 'quarter', or 'year'. Previous three months should be interpreted as a quarter."
        RULE__COUNTRY = "All COUNTRY names must be converted to 2 character ISO country codes"
        RULE__METRIC = "METRIC must be one of 'NSV' or 'NR'"

        # setup the template spec
        default = {
            "name": "acme_gpt",
            "topk": 5,
            "context": [
                "these queries are about cross-border financial transactions (traffic) at a fintech company",
                "'financial institutions' are also known as banks",
                "GSV is a metric measuring sales volume",
                "NSV is a metric measuring sales volume",
                "NR is a metric measuring revenue"
            ],
            "templates": [
                {
                    "template": "how many partners went live over the past TIME_PERIOD",
                    "metadata": {
                        "key": "new_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what new B2B partners went live over the past TIME_PERIOD",
                    "metadata": {
                        "key": "new_b2b_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "which new source and/or destination countries have been launched this TIME_PERIOD",
                    "metadata": {
                        "key": "new_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the trend of SOURCE_COUNTRY to DESTINATION_COUNTRY traffic over the last TIME_PERIOD",
                    "metadata": {
                        "key": "traffic_trend|SOURCE_COUNTRY|DESTINATION_COUNTRY|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all partners in COUNTRY",
                    "metadata": {
                        "key": "partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all source partners in COUNTRY",
                    "metadata": {
                        "key": "source_partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of all destination partners in COUNTRY",
                    "metadata": {
                        "key": "dest_partners|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what is the list of 'financial institutions' in COUNTRY",
                    "metadata": {
                        "key": "banks|COUNTRY",
                        "rules": [
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "how many senders and/or receivers have been serviced this TIME_PERIOD",
                    "metadata": {
                        "key": "active_sndrs_rcvrs|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the expected/projected sales metrics for this TIME_PERIOD",
                    "metadata": {
                        "key": "expected_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the total sales for this TIME_PERIOD",
                    "metadata": {
                        "key": "current_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what is the total revenue for this TIME_PERIOD",
                    "metadata": {
                        "key": "current_sales|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "rank destination countries based on METRIC from SOURCE_COUNTRY",
                    "metadata": {
                        "key": "rank_dest_countries_from_source_country|METRIC|SOURCE_COUNTRY",
                        "rules": [
                            RULE__METRIC,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "rank source partners based on METRIC from SOURCE_COUNTRY",
                    "metadata": {
                        "key": "rank_source_partners_from_source_country|METRIC|SOURCE_COUNTRY",
                        "rules": [
                            RULE__METRIC,
                            RULE__COUNTRY
                        ],
                    }
                },
                {
                    "template": "what was the sales volumes generated from new partners this TIME_PERIOD",
                    "metadata": {
                        "key": "sales_new_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "from how many countries were transactions received this TIME_PERIOD",
                    "metadata": {
                        "key": "source_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "to how many countries were transactions sent this TIME_PERIOD",
                    "metadata": {
                        "key": "dest_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the highlights of business performance this TIME_PERIOD vs. last TIME_PERIOD",
                    "metadata": {
                        "key": "highlights|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the destination countries which were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_destination_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the destination partners which were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_destination_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the source countries that were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_source_countries|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
                {
                    "template": "what are the source partners who were inactive over the last TIME_PERIOD",
                    "metadata": {
                        "key": "inactive_source_partners|TIME_PERIOD",
                        "rules": [
                            RULE__TIME_PERIOD
                        ],
                    }
                },
            ]
        }

        return default

    # test query set
    queries = [
        "what is the trend of traffic over the previous year going from america to ghana?",
        "show me traffic growth from england to india past year?",
        "traffic trend, uk to in, last year?",
        "what are the banks in Korea?",
        "what was the NR, NSV generated from new partners this year?",
        "to which countries were txns sent this year?",
        "summarize the business highlights for the year",
        "what is the total GSV this year?",
        "what is the total NSV this year?",
        "what is the total revenue this year?",
        "how many new partners were added last quarter?",
        "how many tigers were at the zoo?",
        "list the destination countries which had traffic previously, but not in the last month",
        "give me projected NR and NSV this month?",
    ]

    # vars
    index_name = "acme_gpt_index"
    persist_directory = "chromadb123"
    agent_name = "acme_gpt"

    # create an agent
    agent = LLMQueryMapper(name=agent_name,
                            platform="openai")

    # load spec
    spec = get_profilespec()
    agent.load_spec(spec=spec,
                    persist_directory=persist_directory,
                    index_name=index_name)

    # test the queries
    for query in queries:
        result = agent.query(query, spec)
        if result.get("success"):
            key = result.get("key")
            print (f"Query: {query}\nKEY: {key}\n")
        else:
            suggestions = result.get("suggestions")
            print (f"Query: {query}\nSuggestions: {suggestions}\n")
