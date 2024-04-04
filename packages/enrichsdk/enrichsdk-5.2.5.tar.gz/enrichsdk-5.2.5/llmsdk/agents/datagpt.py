import io
import re
import os
import time
import json
import hashlib
import sqlite3
import datetime
import pandas as pd
from contextlib import redirect_stdout

from langchain.agents import create_sql_agent
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor

from . import agent_events
from llmsdk.lib import SafeEncoder
from llmsdk.services.log import *


class LLMDataQuerier(object):
    """
    Class to do querying of a dataframe using LLMs
    """

    def __init__(self,
                 name,
                 cred,
                 mode,
                 data,
                 cascade,
                 debug=False):
        """
        init the dataframe LLM query agent
        name: name of the agent
        cred: credentials object
        mode: type of input dataset
                'csv': data will be available as path to a csv
                'sqlite': data will be available as path to a sqlite db
                'df': data will be available as pandas dataframe
        data: pointer to data, see mode param
        cascade: list of LLM backends to use
                    the list will be tried in order for each query
                    on failure, the next LLM in the list will be tried
        debug: if True, returns a bunch of useful information for debugging
        """
        start_time = time.time()

        # logging
        self.logger = get_logger()

        # defaults
        self.max_llm_tokens = 1024 # max tokens in the response
        self.mode = mode
        self.data = data
        self.debug = debug

        # name
        self.agent_name = name

        # creds
        self.cred = cred
        # LLM params
        self.cascade = cascade

        # init the llm objects
        self.llms = self._get_llm_objs(cascade=self.cascade, cred=self.cred)

        # init the agents
        self.agents = self._get_agent(mode=self.mode, data=self.data)

        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "cascade": self.cascade,
                "mode": self.mode,
                "data": f"dataframe of shape {self.data.shape}" if self.mode=='df' else self.data,
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
            "timestamp": round(ts, 3),
            "duration": round(duration, 3),
            "name": event_name,
            "params": params,
        }
        self.metadata['events'].append(event)

        return event

    def _get_llm_objs(self, cascade, cred):
        # init the LLM models
        ##
        ## cascade = [{"platform": platform, "model": model}, ...]
        ##

        # run through each entry in the LLM cascade

        llms = []
        for entry in cascade:
            # get the platform name
            _id = entry.get("id")
            if _id is None:
                self.logger.warn("Cannot init LLM in cascade, no ID",
                             extra={
                                 'source': self.agent_name,
                                 'data': entry
                             })
                continue

            # we can proceed
            platform = entry.get("platform")

            if platform == "openai":
                # get the api key from creds
                api_key = self._get_api_key(cred, platform)

                ###
                # langchain indiosyncracy
                # needed for the SQL agent later on
                #
                if platform == 'openai' and api_key is not None:
                    os.environ['OPENAI_API_KEY'] = api_key

                ###

                # get the llm objects
                model = entry.get("model")
                if model in ["gpt-3"]:
                    # non-chat models
                    llm = OpenAI(temperature=0,
                                           model=model,
                                           max_tokens=self.max_llm_tokens,
                                           openai_api_key=api_key)
                elif model in ["gpt-3.5-turbo", "gpt-4"]:
                    # chat models
                    llm = ChatOpenAI(temperature=0,
                                               model=model,
                                               max_tokens=self.max_llm_tokens,
                                               openai_api_key=api_key)
                else:
                    self.logger.warn("Cannot init LLM in cascade, unknown model",
                             extra={
                                 'source': self.agent_name,
                                 'data': entry
                             })
                    continue

                # add the LLM backend to the list
                llm_backend = {
                    "id": _id,
                    "platform": platform,
                    "model": model,
                    "llm": llm
                }
                llms.append(llm_backend)

            else:
                self.logger.warn("Cannot init LLM in cascade, unknown platform",
                             extra={
                                 'source': self.agent_name,
                                 'data': entry
                             })

        if len(llms) == 0:
            raise Exception("No LLMs initialized, cannot proceed")

        return llms

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

    def _construct_sqlagent_prompt(self, data):
        """
        construct prompt for the SQL agent
        give as much context as possible to help the LLM
        """
        # construct table schema
        tables = data.get("tables", [])
        num_tables = len(tables)

        table_stmt = f"The database has {num_tables} table(s). The tables and corresponding columns are as follows:" + "\n"

        for table in tables:
            table_name = table['name']
            table_desc = table['desc']
            cols = table["cols"]

            cols_text = []
            for col in cols:
                col_name = list(col)[0]
                col_desc = col[col_name]
                cols_text.append(f"\t{col_name}: {col_desc}")
            cols_text = ",\n".join(cols_text)

            # add the table context helpers
            table_context = table['context']
            table_context = [f"- {context}" for context in table_context]
            table_context = "\n".join(table_context)

            table_stmt += f"""
TABLE NAME: {table_name}
TABLE DESCRIPTION: {table_desc}
COLUMN names and descriptions:
{cols_text}

Keep the following context in mind when querying the {table_name} table:
{table_context}
"""

        # get the date for the agent
        x = datetime.datetime.now()
        today = x.strftime("%A, %B %d, %Y")

        SQL_PREFIX = f"""You are an agent designed to interact with a SQL database.

{table_stmt}

Your task is as follows:
Given an input question, create a syntactically correct {{dialect}} query to run, then look at the results of the query and return the answer.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.

You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

Ensure that you follow these rules:
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
- If the answer contains multiple items, format the answer as a json list.
- If you need to do string comparisons, always use the LOWER() function.
- If you need the date to answer any questions, remember that today is {today}.
- If the question does not seem to be related to the database, just return "I don't know" as the answer.
"""

        return SQL_PREFIX


    def _get_agent(self, mode, data):
        """
        init the agent
        """

        mode = data.get("mode")
        dataset = data.get("dataset")

        # check for valid mode
        if mode not in ['sql', 'csv', 'df']:
            raise Exception("Unsupported mode for input data")

        # setup agent for sql
        if mode == 'sql':
            # setup the DB conn
            db = SQLDatabase.from_uri(f"sqlite:///{dataset}")

            # override LangChain SQL agent prompt prefix
            # so that the agent doesn't use LIMIT statements
            SQL_PREFIX = self._construct_sqlagent_prompt(data)

        # setup agent for dataframes
        elif mode == 'csv':
            # Handle bad quality csv as well..
            df = pd.read_csv(data, on_bad_lines='skip', encoding='unicode_escape')
        elif mode == 'df':
            df = data
        else:
            raise Exception(f"Unsupported mode: {mode}")

        # finally, create one agent per LLM backend
        agents = {}
        for llm_backend in self.llms:
            # get the llm object
            llm = llm_backend['llm']
            # for csv agents
            if mode in ['csv', 'df']:
                agent = create_pandas_dataframe_agent(llm=llm,
                                                        df=df,
                                                        verbose=True)
            # for sql agents
            elif mode in ['sql']:
                toolkit = SQLDatabaseToolkit(db=db, llm=llm)
                agent = create_sql_agent(llm=llm,
                                            toolkit=toolkit,
                                            prefix=SQL_PREFIX,
                                            verbose=True)
            # force intermediate steps on return
            # we use this to get the agent's chain of thought
            agent.return_intermediate_steps = True
            # agent object
            agent_obj = {
                "platform": llm_backend['platform'],
                "model": llm_backend['model'],
                "agent": agent,
            }
            _id = llm_backend['id']
            agents[_id] = agent_obj

        return agents

    def _get_dialect(self, mode=None):
        """
        return the code dialect given the agent's mode
        """
        dialects = {
            "sql": "sql",
            "df": "pandas",
            "csv": "pandas",
        }
        if not mode:
            mode = self.mode
        dialect = dialects.get(mode)

        return dialect

    def _parse_code_from_thought(self, thoughts):
        """
        parse the chain-of-thought information sent by the LLM for the code snippets
        """
        # get the dialect of the code
        dialect = self._get_dialect()

        snippets = []
        # step through each thought, but in reverse order
        # keep storing successful thoughts
        # when we hit the first failure, we break out
        thoughts.reverse()
        for one_step in thoughts:
            # check by dialect
            if dialect == 'sql':
                # get the components
                tool = one_step['tool'].lower()
                tool_input = one_step['tool_input'] # don't lowercase
                observation = one_step['observation'].lower()
                # get the code snippet
                if tool == 'sql_db_query' and "error: (sqlite3.operationalerror)" not in observation:
                    snippets.append(tool_input)
                if tool == 'sql_db_query' and "error: (sqlite3.operationalerror)" in observation:
                    # we have found a failure
                    # most likely, the LLM would have failed
                    # upto this point
                    # so we can break
                    break
            if dialect == 'pandas':
                # get the components
                tool = one_step['tool'].lower()
                tool_input = one_step['tool_input'] # don't lowercase
                # get the code snippet
                if tool == 'python_repl_ast':
                    snippets.append(tool_input)

        thoughts.reverse() # reverse the thoughts list for consistency with input
        snippets.reverse() # we need the reverse order now
        code = {
            "dialect": dialect,
            "snippets":  snippets
        }

        return code

    def _get_chain_of_thought(self, result):
        """
        parse the intermediate steps list
        to construct human-readable chain-of-thought
        of the agent working through its solution
        """
        thoughts = []

        # get the dialect of the code
        dialect = self._get_dialect()

        # get the intermediate steps
        steps = result.get("intermediate_steps", [])

        # foreach step
        for step in steps:
            agent_action = step[0]
            observation = step[1]

            tool = agent_action.tool
            tool_input = agent_action.tool_input
            log = agent_action.log

            # get the thought
            m = None
            if dialect == "sql":
                m = re.search('^(.+?)\s+?Action:', log, flags=re.IGNORECASE)
            elif dialect == "pandas":
                m = re.search('^Thought(.+?)\s+?Action:', log, flags=re.IGNORECASE)
            if m:
                thought = m.group(1).strip()
            else:
                thought = "BEGIN"

            # contruct the ReACT step
            one_step = {
                "thought": thought,
                "tool": tool,
                "tool_input": tool_input,
                "observation": observation,
            }
            thoughts.append(one_step)

        return thoughts

    def _is_json(self, string):
        """
        check if string is json
        """
        try:
            json.loads(string)
        except ValueError as e:
            return False
        return True

    def _err_msg(self, t):
        msgs = {
            "err": "I'm having trouble understanding. Try another way of wording your query."
        }
        return msgs.get(t, "Something went wrong, try your query again.")

    # interfaces

    def get_metadata(self):
        """
        return metadata collected by the agent
        """
        return self.metadata

    def mux_query_one_try(self, query, agent_id, agent):
        """
        do one try of the query through a specified agent in the cascade chain
        """
        # get the llm backend
        agent_exec = agent['agent']

        try:
            # redirect stdout so we can capture the agent's chain-of-thought
            # this is a hack until we figure out how to get chain-of-thought
            # directly from LangChain
            f = io.StringIO()
            with redirect_stdout(f):
                result = agent_exec(query)
            thought = f.getvalue()
            # check if LLM could not find solution
            if result['output'].lower() == "i don't know.":
                raise Exception("Force exception")
        except:
            # something went wrong when trying the query
            result = { "input": query, "output": self._err_msg('err')}
            thought = ""
            success = False
        else:
            success = True
            result['cascade'] = { "id": agent_id }
            for key in ['platform', 'model']:
                result['cascade'][key] = agent[key]


        return success, result, thought


    def query(self, query, cascade_id=None):
        """
        run a query on the dataframe
        query: query string
        cascade_id: id of the model to use in the cascade list specified during agent init
        """
        start_time = time.time()

        seq = 0
        tries = []
        if cascade_id == None:
            # we have not specified an agent id
            # in the cascade list so try them all
            for _id, agent in self.agents.items():
                # try one agent in the cascade
                success, result, thought = self.mux_query_one_try(query, _id, agent)
                tries.append({"seq": seq, "cascade_id": _id, "success": success})
                seq += 1
                if success:
                    break
        else:
            # we have specified an agent id
            # in the cascade list so try only that
            agent = self.agents.get(cascade_id)
            if not agent:
                raise Exception(f"Unknown agent ID {cascade_id}, not specified in cascade")

            # try the requested agent in the cascade
            success, result, thought = self.mux_query_one_try(query, cascade_id, agent)
            tries.append({"seq": seq, "cascade_id": cascade_id, "success": success})

        result['success'] = success
        result['tries'] = tries

        # format the result keys
        if result.get('input'):
            result['query'] = result.pop('input')
        if result.get('output'):
            result['answer'] = result.pop('output')
        result['intermediate_steps'] = [] if 'intermediate_steps' not in result else result['intermediate_steps']

        # check for result type
        is_json = self._is_json(result['answer'])
        if is_json:
            result['answer'] = json.loads(result['answer'])
            result['type'] = 'json'
        else:
            result['type'] = 'str'

        # get the chain of thought
        # strip ANSI control sequences first
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        thought = ansi_escape.sub('', thought)
        # get line-by-line chain of thought from stdout
        result['raw_thoughts'] = thought.split("\n")

        # convert intermediate steps to chain of thought
        # this is more stable
        result['chain_of_thought'] = self._get_chain_of_thought(result)

        # get the code snippets from the chain of thought
        # result['code'] = self._parse_code_from_rawthought(result['raw_thoughts'])
        result['code'] = self._parse_code_from_thought(result['chain_of_thought'])

        # log the event
        params = {
            "query": query,
            "cascade_id": cascade_id,
            "result": result.copy() if isinstance(result, dict) else result
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

        # decide on what fields to return
        # we do it after the logging so that logs have everything
        if not self.debug:
            r = result.pop('raw_thoughts')
            r = result.pop('intermediate_steps')

        return result




if __name__ == "__main__":

    cred = None
    customer = "acme_2"
    # dbpath = '.../file.sqlite'    # if using SQLite DB
    # csvpath = '.../file.csv'      # if using CSV
    # df = pd.read_csv(csvpath)     # if using raw Pandas DF
    # csvpath = os.path.expandvars("$DATA_ROOT/$AGENTNAME/acme_1/revenue.dashboard_market.csv")
    # df = pd.read_csv(csvpath)     # if using raw Pandas DF

    def get_llm_cascade():
        llm_cascade = [
            {"id": "economy", "platform": "openai", "model": "gpt-3.5-turbo"},
            {"id": "power", "platform": "openai", "model": "gpt-4"},
        ]
        return llm_cascade

    def get_dataset(customer, dbpath):
        data = {
            "acme_1": {
                "mode": "sql",
                "dataset": dbpath,
                "tables": [
                    {
                        "name": "disha",
                        "desc": "contains information about currency transfers between partners across countries",
                        "context": [
                            "each row in the table includes multiple transactions",
                            "when querying for month columns, always use a two-digit month number (e.g. June will be 06 instead of 6)"
                        ],
                        "cols": [
                            {"year": "year during which the transaction occured"},
                            {"month": "two-digit month number in which the transaction occured"},
                            {"source_partner": "name of the partner who sent the transaction"},
                            {"destination_partner": "name of the partner who received the transaction"},
                            {"source_country": "country from which the transaction was sent"},
                            {"destination_country": "country in which the transaction was received"},
                            {"financial_institution": "name of the financial institution that sent the transaction"},
                            {"destination_currency": "currency code in which the transaction occured"},
                            {"net_sales": "total net sales volume"},
                            {"net_revenue": "total net revenue"},
                            {"successful_txns": "total number of successful transactions"},
                            {"failed_txns": "total number of failed transactions"},
                            {"is_new_partner": "binary field indicating whether the source partner is a new partner"},
                            {"is_new_country": "binary field indicating whether the source country is a new country"},
                            {"b2b": "binary field indicating whether the source partner is a B2B partner"}
                        ]
                    }
                ]
            },
            "acme_2": {
                "mode": "sql",
                "dataset": dbpath,
                "tables": [
                    {
                        "name": "surveyresults",
                        "desc": "contains information on sentiment scores for products across various segments of survey respondents",
                        "context": [
                            "a segment is defined as the combination of the country, gender, and age_range columns",
                            "when asked to provide interesting insights, respond with the following statistics in bullet point format - top 3 and bottom 3 segments, product with highest sentiment score, product with highest sentiment score among women but lowest sentiment score among men",
                            "when asked to summarize the dataset, provide your response in bullet point format"
                        ],
                        "cols": [
                            {"product_id": "system identifier for product being surveyed"},
                            {"country": "country to which survey respondent belongs"},
                            {"gender": "gender of respondent (female, male)"},
                            {"age_range": "age range bucket into which survey respondent falls (under 18, 18 to 24, 25 to 34, 35 to 44, 45 to 54, above 55)"},
                            {"sentiment_score": "integer number indicating sentiment or affinity of a segment of survey respondents to the product (range is 50 to 100, higher score are more positive sentiment)"},
                            {"le_score": "float number indicating line efficiency score of a segment of survey respondents to the product"},
                            {"overall_score": "float number indicating importance score of a product"},
                        ]
                    }
                ]
            },
        }
        return data[customer]

    # (query, cascade_id)
    queries = {
        "acme_1": [
            ("how many transactions were made this year?", None),
            ("how many transactions were made this year?", "power"),
            ("from how many countries were txns sent this month last year?", None),
            ("how many partners have been serviced this month and year?", None),
            ("how many partners have been serviced this month and year?", "power"),
            ("who are all the new source partners this year", "economy"),
            ("who are all the new source partners this year", None),
            ("what was the total revenue generated from new partners this year", None),
            ("list the top 10 financial institutions by revenue sending transactions to Egypt", None),
            ("list all new b2b partners this year", None),
            ("list all partners in India", None)
        ],
        "acme_2": [
            ("what product and segment shows the highest sentiment?", None),
            ("what are the top 3 products in the US for women between 18 and 24?", None),
            ("what is the top segment for each product?", None),
            ("what is the top product in the US for older women?", None),
            ("what are some interesting insights on this dataset?", "power")
        ],
    }

    # get the dataset spec
    dataset = get_dataset(customer, dbpath)
    # get the cascade chain spec
    cascade = get_llm_cascade()

    # setup the agent and ask questions
    agent = LLMDataQuerier(name="datagpt",
                           cred=cred,
                           mode='sql',
                           data=dataset,
                           cascade=cascade,
                           debug=False)

    # answers
    for entry in queries[customer]:
        query = entry[0]
        cascade_id = entry[1]
        result = agent.query(query=query, cascade_id=cascade_id)
        print(f"QUESTION (cascade_id={cascade_id}): {query}")
        print(f"ANSWER: {result.get('answer')}")
        print(f"METADATA: {json.dumps(result, indent=4, cls=SafeEncoder)}")
        print("\n----------\n")
