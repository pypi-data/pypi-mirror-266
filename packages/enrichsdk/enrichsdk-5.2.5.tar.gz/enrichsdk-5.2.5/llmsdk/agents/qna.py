import os
import json
import time
from collections import defaultdict

from langchain import LLMChain
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationTokenBufferMemory, ConversationKGMemory
from langchain.callbacks import get_openai_callback

from . import agent_events
from llmsdk.agents.basellm import BaseLLMAgent


__all__ = ['LLMIndexQuerier']


class LLMIndexQuerier(BaseLLMAgent):
    """
    Class to do querying using LLMs
    Query can be run against a specified set of documents that act
    as context to constrain the answers
    or against all the stored knowledge of the LLM model
    """

    def __init__(self,
                 name,
                 cred={},
                 platform="openai",
                 searchapi="serpapi",
                 statestore="redis",
                 memory_size=1000):
        """
        init the LLM query agent
        name: name of the agent
        cred: credentials object
        platform: name of the platform backend to use
                default to OpenAI GPT model for now, and Azure as well
                will be extended in the future to suuport other models
        memory_size: how many tokens of memory to use when chatting with the LLM
        """

        start_time = time.time()

        # init the base class
        super().__init__(name=name,
                         cred=cred,
                         platform=platform,
                         agent_type="qna",
                         searchapi=searchapi,
                         statestore=statestore,
                         memory_size=memory_size)

        # defaults
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.index = None
        self.latest_context = []
        self.context_topK = 1
        self.current_kg = []
        self.metadata = {}
        self.vdb_client = None
        self.index_name = None
        self.index_store = None
        self.state_store = statestore
        self.docs = {}

        # LLM params
        self.platform = platform
        self.searchapi = searchapi
        self.chaintype = "stuff"
        self.memory_size = memory_size

        # init the memories for the llm
        conv_memory = ConversationTokenBufferMemory(llm=self.llm,
                                                    max_token_limit=self.memory_size,
                                                    memory_key="chat_history",
                                                    input_key="input",
                                                    return_messages=True)
        kg_memory = ConversationKGMemory(llm=self.llm,
                                         return_messages=True)
        self.memory = conv_memory
        self.kg = kg_memory

        # init the QnA chain for internal queries
        prompt = self._get_query_prompt_internal()
        self.llm_chain_int = load_qa_chain(llm=self.llm,
                                           chain_type=self.chaintype,
                                           memory=self.memory,
                                           prompt=prompt)
        # init the chain for external queries
        prompt = self._get_query_prompt_external()
        self.llm_chain_ext = LLMChain(llm=self.llm,
                                      prompt=prompt)
        # init the chain for kwords
        prompt = self._get_query_prompt_kwords()
        self.llm_chain_kw = LLMChain(llm=self.llm,
                                      prompt=prompt)
        # init the chain for suggestions
        prompt = self._get_query_prompt_suggest()
        self.llm_chain_sug = LLMChain(llm=self.llm,
                                      memory=self.memory,
                                      prompt=prompt)
        # init the agent for searches
        self.llm_agent_srch, self.searchengine = self._load_search_agent(cred=self.cred,
                                                      searchapi=self.searchapi,
                                                      llm=self.llm)
        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "type": self.agent_type,
                "id": self.agent_id,
                "platform": self.platform,
                "searchapi": self.searchapi,
                "statestore": self.state_store,
                "memory_size": self.memory_size,
                "chaintype": self.chaintype,
            },
            "events": []
        }
        # log that the agent is ready
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_READY, duration)

    ## helper functions

    def _get_query_prompt_internal(self):
        """
        generate a prompt for running a query in internal mode
        """
        template = """You are a helpful and diligent chatbot having a conversation with a human.
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say 'I am not sure', don't try to make up an answer.
If the question is framed in active voice, first convert it to passive voice and use that to answer the question.

        {context}

        {chat_history}
        Human: {input}
        Chatbot:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "input", "context"],
            template=template
        )

        return prompt

    def _get_query_prompt_external(self):
        """
        generate a prompt for running a query in external mode
        """
        template = """In the context of the following terms: {context},

        {input}"""

        prompt = PromptTemplate(
            input_variables=["context", "input"],
            template=template
        )

        return prompt

    def _get_query_prompt_suggest(self):
        """
        generate a prompt for running a query to suggest other ways of asking a question
        given some chat history
        """
        template = """You are a helpful and diligent chatbot having a conversation with a human.
        Your task is to only suggest some alternate ways to pose the last question based on the context in the chat history.
        Format your response as a json list only.

        {chat_history}
        Human: {input}
        Chatbot:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "input"],
            template=template
        )

        return prompt

    def _get_query_prompt_kwords(self, context=""):
        """
        generate a prompt for extracting keywords from a paragraph
        """
        template = """You are the chief of staff to a busy executive. You will be given a paragraph of text
        and must identify a few (maximum of 5) key phrases from the paragraph. Do not summarize what you find,
        respond with the key phrases exactly. Structure your response as a json list exactly.
        DO NOT RESPOND WITH ANY KEY PHRASES FROM CONTENT ABOVE THIS LINE.

        Here is the paragraph:
        {context}

        The key phrases are:
        """

        prompt = PromptTemplate(
            input_variables=["context"],
            template=template,
        )

        return prompt

    def _list_to_nested_dict(self, l):
        """
        take a list and return a nested dict
        used only for formating the KG entities
        """
        # loop through them to construct the dict
        rd = defaultdict(lambda: defaultdict(list))
        for e in l:
            # get constiuents
            subject = e[0]
            predicate = e[1]
            object_ = e[2]

            # format the output
            rd[subject][predicate].append(object_)

        def default_to_regular(d):
            if isinstance(d, defaultdict):
                d = {k: default_to_regular(v) for k, v in d.items()}
            return d

        return default_to_regular(rd)

    ## interfaces

    def run_query_internal(self, query):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # get the similar docs
        docs = self.get_similar_docs(query)

        if docs is None:
            return {
                "question": query,
                "answer": "Could not find document chunks to process"
            }

        # setup the QnA chain object
        response = self.llm_chain_int({"input_documents":docs, "input":query},
                                    return_only_outputs=False)

        # run the query against the similar docs
        result = {
            "question": query,
            "answer": response.get('output_text', self._err_msg('field')).strip(),
            "sources": [{"content": d.page_content, "metadata": d.metadata, "distance": d.metadata.pop('distance')} for d in docs],
        }

        # check if suggest call is needed
        if ('output_text' not in response) or ("i am not sure" in result['answer'].lower()):
            response = self.run_query_suggest(query)
            result['suggest'] = response['suggest']
            # we don't have a usable answer, so no need for sources
            result['sources'] = []

        return result

    def run_query_external(self, query):
        """
        run a query using llm
        this is useful when looking for answers that generic llm can provide
        """
        # augment the query with some context to guide the LLM
        context = ", ".join(self.latest_context)
        result = self.llm_chain_ext({"context": context, "input":query},
                                    return_only_outputs=True)
        result = {
            "question": query,
            "answer": result,
            "sources": [{"source": f"llm-{self.platform}"}]
        }

        return result

    def run_query_search(self, query):
        """
        run a query using the search agent
        this is useful when looking for answers using a search engine
        """
        def extract_content_sources(sourcedata):
            docs = sourcedata.get('organic_results')
            if not docs:
                return None
            sources = [{"content": d.get('snippet', ""), "source": d.get('link')} for d in docs]
            return sources

        # modify the query using context history
        context = ", ".join(self.latest_context)
        query_mod = f"In the context of {context}, {query}"

        # get the human-readable result
        result = self.llm_agent_srch.run(input=query_mod)

        # get the sources
        sourcedata = self.searchengine.results(query_mod)
        sources = extract_content_sources(sourcedata)
        if not sources:
            sources = [{"content": "", "source": f"search-{self.searchapi}"}]

        # construct result
        result = {
            "question": query,
            "answer": result,
            "suggest": list(set([q.get('question', '') for q in sourcedata.get('related_questions', [])])),
            "sources": sources
        }

        return result

    def run_query_suggest(self, query):
        """
        run a query using llm to suggest other ways of asking the query,
        in the context of the chat history
        """
        # augment the query with some context to guide the LLM
        response = self.llm_chain_sug({"input":query},
                                      return_only_outputs=True)
        result = response.get('text', response).strip()
        try:
            # we asked the LLM to give us json
            suggest = json.loads(result)
            # in case the LLM gave us a list of dicts instead of list of strs
            suggest = [list(s.values())[0] if isinstance(s, dict) else s for s in suggest]
        except:
            suggest = []

        result = {
            "question": query,
            "answer": result,
            "suggest": suggest,
            "sources": [{"source": f"llm-{self.platform}"}]
        }

        return result

    def run_query_kwords(self, context=""):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers that generic llm can provide
        """
        result = self.llm_chain_kw({"context": context},
                                    return_only_outputs=True)
        result = result.get('text', result)
        # a few tries to extract the response
        # sometimes, the LLM messes up
        try:
            result = json.loads(result)
        except:
            try:
                result = json.loads(f"[{result.split('[')[-1]}")
            except:
                try:
                    result = result.split("\n")
                    result = [r.replace("- ", "") for r in result]
                except:
                    pass

        # force a list
        result = [] if not isinstance(result, list) else result

        return result

    def extract_add_kg_entities(self, answer):
        """
        extract all KG entities, format as {entity: relation}
        and add to the current set of tracked KG entities
        """
        # get the KG entities for this answer
        kg_entities = self.kg.get_knowledge_triplets(answer)
        # format the entities as we need them
        kge = [(e.subject, e.predicate, e.object_) for e in kg_entities]

        ## -- TO-DO --
        # at this point
        # we will have to do some post-processing on the KG entities
        # one option is to look at useful relations
        # defined by the predicate
        # e.g. {"is defined as", "shall mean", "is"} -> "="
        ## -- END TO-DO --

        # add to running list of all KG entities
        self.current_kg += kge

        # format for output
        kge = self._list_to_nested_dict(kge)

        return kge

    def get_kg_entities(self):
        """
        return all the KG entities as a dict
        {entity: (relation, object)}
        """
        # get the current list of KG entities
        kg_entities = self._list_to_nested_dict(self.current_kg)

        return kg_entities


    def query(self, query, mode="internal", policy={}):
        """
        run a query on an index using an llm chain object
        query: query string
        mode: 'internal' for querying over docset,
              'external' for general query,
              'suggest' for asking the LLM for alternate ways to pose the question
        policy: any extra params needed by the agent
        """

        start_time = time.time()

        # check to see if we need to reset agent memory
        reset_state = policy.get("reset_state", False)
        if reset_state:
            # clear the agent state
            self.clear_agent_state()
        else:
            # set the state of the agent
            # this happens only if we are not doing a reset-state
            self.set_agent_state(statekey=self.statekey)

        method = getattr(self, f"run_query_{mode}", None)
        if method is None:
            raise Exception(f"Unsupported mode: {mode}")

        if self.platform in ['openai', 'azure']:
            with get_openai_callback() as cb:
                result = method(query)
            stats = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4)
            }
        else:
            result = method(query)
            stats = {}

        if result:

            answer = result['answer']

            if answer:
                # add keywords identified to the result
                result['keywords'] = self.run_query_kwords(context=answer)

                # store the latest context
                # this is useful to guide the external agent
                # since it is memory-less
                # only store the top-n keywords
                # storing more will make the LLM overfit responses
                self.latest_context = result['keywords'][0:self.context_topK]

                # add KG elements to the result
                result['kg'] = self.extract_add_kg_entities(answer)

        # store the agent's state
        self.store_agent_state()

        # log the event
        params = {
            "query": query,
            "mode": mode,
            "policy": policy,
            "result": result.copy() if result is not None else None,
            "stats": stats
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

        # add the event to the result
        if result:
            result['metadata'] = {
                "timestamp": event['timestamp'],
                "duration": event['duration'],
                "stats": stats
            }

        return result


if __name__ == "__main__":

    dirpath = '...'
    index_name = "bf_index"
    persist_directory = "chromadb123"

    queries = [
        "what are the top heavy rules?",
        "which mortality table to use for top heavy rules?",
        "tell me about plan termination",
        "tell me about the retirement plan termination",
        "are there any death benefits?",
        "explain employer contributions",
        "are there any participant contributions needed?",
        "explain participant contributions",
        "who is optimus prime?",
        "tell me about the benefits committee",
        "what is the expansion of UCN?",
        "what is the expansion of UCN? if the answer is not found in the documents, say so",
        "what is the definition of a plan participant?",
        "what sections mention the retirement age?",
        "what is the retirement age?",
        "are there clauses for the retirement age?",
        "how is the pension calculated?"
    ]
    query = queries[-1]

    # setup the agent and the index
    agent = LLMIndexQuerier(name="agent_bf", platform="azure")
    # point it to the data
    # data = agent.load_data(source="dir",
    #                        content=dirpath,
    #                        params={"glob":"**/*.*"})
    data = agent.load_data(content=dirpath)

    # create the index
    agent.create_add_index(data=data,
                           store="chroma",
                           persist_directory=persist_directory,
                           index_name=index_name)

    # start asking questions
    query = "what is the deadline for prelim quotes?"

    # internal mode
    # run query against the index
    result = agent.query(query, mode="internal")
    print ("Internal:")
    print (json.dumps(result, indent=4))

    # # external mode
    # # run query against world knowledge
    # result = agent.query(query, mode="search")
    # query = "tell me about that table"
    # print ("Search:")
    # print (json.dumps(result, indent=4))
    #
    # # internal mode
    # # run query against the index
    # query = "who is optimus prime?"
    # result = agent.query(query, mode="internal")
    # print ("Internal with suggestions:")
    # print (json.dumps(result, indent=4))
    #
    # # suggest mode
    # # run query against the index
    # # clear the memory of the agent to simulate a new session of QnA
    # policy = {
    #     "reset_state": True
    # }
    # query = "What is the situs state for this plan?"
    # result = agent.query(query, mode="suggest", policy=policy)
    # print ("Suggestions:")
    # print (json.dumps(result, indent=4))
    #
    # # get the current set of KG entities
    # kg_entities = agent.get_kg_entities()
    # print ("KG:")
    # print(json.dumps(kg_entities, indent=4))

    # get the current metadata
    metadata = agent.get_metadata()
    print ("Metadata:")
    print(json.dumps(metadata, indent=4))
