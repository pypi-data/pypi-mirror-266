import json
import time
import string
from re import sub

from langchain import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback

from . import agent_events
from llmsdk.agents.basellm import BaseLLMAgent
from ..lib import extractors
from llmsdk.lib import SafeEncoder

__all__ = ['LLMMultiStepAgent']

class LLMMultiStepAgent(BaseLLMAgent):
    """
    Class to do multi-step actions using LLMs
    Step can include RAG, simple prompting, tool use, and more
    """

    def __init__(self,
                 name,
                 cred={},
                 platform="openai",
                 searchapi="serpapi",
                 statestore="redis",
                 topk=7):
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
                         agent_type="multistep",
                         searchapi=searchapi,
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
        self.searchapi = searchapi

        # init the llm and embeddings objects
        self.llm, self.embeddings = self._get_llm_objs(platform=self.platform,
                                                       cred=self.cred)

        # init the agent for searches
        self.llm_agent_srch, self.searchengine = self._load_search_agent(cred=self.cred,
                                                                          searchapi=self.searchapi,
                                                                          llm=self.llm)
        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "name": self.agent_type,
                "platform": self.platform,
                "chaintype": self.chaintype,
            },
            "events": []
        }
        # log that the agent is ready
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_READY, duration)

    ## helper functions

    def _get_query_prompt_internal(self, docs, query, context, instructions):
        """
        generate a prompt for running a query in internal mode
        """
        sys_msg = """You are a highly advanced AI program designed to extract specific pieces of information from business documents.
Be precise in the responses you provide. Do not respond in full sentences, but only with the specific information asked for.
You will be provided with relevant pieces of context extracted from a business document to answer the question at the end.
If the question asks you to format your answer in some specific manner, do so.
If the question includes instructions to help you with extraction, follow those instructions.
If you cannot find the answer in the context, just say 'unknown', don't try to make up an answer and do not provide any explanations.
"""
        docs = [d.page_content for d in docs]

        human_msg = f"""
------ BEGIN DOCUMENT CONTEXT ------
{docs}
------ END DOCUMENT CONTEXT ------

------ BEGIN QUESTION ------
{context}
{query}
{instructions}
------ END QUESTION ------

Your response:"""

        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=human_msg),
        ]

        return messages

    def _get_query_prompt_norag(self, query, context, instructions):
        """
        generate a prompt for running a query without doing RAG
        """
        sys_msg = f"""You are a highly advanced AI program designed answer questions in natural language.
Your task is to read some text that is given to you and answer all questions about that text.
If you are provided with context to help you answer the question, pay attention to the context.
If the question asks you to format your answer in some specific manner, do so.
If the question includes instructions to help you with your task, follow those instructions exactly.
If you don't know the answer, just say 'unknown', don't try to make up an answer and do not provide any explanations.
"""

        human_msg = f"""
------ BEGIN CONTEXT ------
{context}
------ END CONTEXT ------

------ BEGIN QUESTION ------
{query}
{instructions}
------ END QUESTION ------

Your response:"""

        messages = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=human_msg),
        ]

        return messages

    ## interfaces

    def read_document(self, source, content, metadata={}, params={}, store="chroma", persist_directory=None):
        """
        wrapper function that takes in the path to a document
        and sets it up for reading by the agent
        this function will create a new index if the agent does not already have one
        else it will use the existing index pointer
        needs the persist_directory that the index will use
        """
        # load the document
        data = self.load_data(source=source, content=content)

        # add the document to index
        if not self.index:
            # we have to init a new index
            self.create_add_index(data=data,
                                   store=store,
                                   persist_directory=persist_directory,
                                   index_name=self.agent_name)
        else:
            # we can use the agent's index pointer
            self.add_to_index(data)

        # extract text from document if it is a pdf
        # so that we have the table data
        if source in ["pdf"]:

            # run through Textract
            extracted_data = extract_text_from_file(content, provider="aws")

            # take the Textract output
            # and add tables and linetext to index
            for block in ["tables", "text"]:
                for extract in extracted_data:
                    # for each page in the document
                    for entry in extract[block]:
                        # for each table in the page
                        if any(f not in entry for f in ['id', 'content']):
                            continue
                        metadata = { "source": entry['id'] }
                        data = self.load_data(source="str",
                                               content=entry['content'],
                                               metadata=metadata)
                        self.add_to_index(data)

            # add the signature details to the agent's knowledge
            for extract in extracted_data:
                signatures = extract["signatures"]
                self.doc_signatures.extend(signatures)

        return

    def run_query_search(self, query, context="", instructions=""):
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

        # get the human-readable result
        result = self.llm_agent_srch.run(input=query)

        # get the sources
        sourcedata = self.searchengine.results(query)
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

    def run_query_internal(self, query, context="", instructions=""):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # get the similar docs
        docs = self.get_similar_docs(query, topk=self.topk)

        # construct the prompt
        prompt = self._get_query_prompt_internal(docs, query, context, instructions)

        # call the LLM
        response = self.llm(prompt)

        # run the query against the similar docs
        result = {
            "question": query,
            "answer": response.content,
            "sources": [{"content": d.page_content, "metadata": d.metadata, "distance": d.metadata.pop('distance')} for d in docs],
        }

        return result

    def run_query_norag(self, query, context="", instructions=""):
        """
        run a query using llm to answer questions about some text data
        this is useful when looking for answers about some context but without doing RAG
        """
        # construct the prompt
        prompt = self._get_query_prompt_norag(query, context, instructions)

        # call the LLM
        response = self.llm(prompt)

        result = {
            "question": query,
            "answer": response.content,
        }

        return result

    def query(self, query, context="", instructions="", mode="internal"):
        """
        run a query on an index using an llm chain object
        query: query string
        mode: 'internal' for querying over docset, 'search' for searching the web
        """

        start_time = time.time()

        method = getattr(self, f"run_query_{mode}", None)
        if method is None:
            raise Exception(f"Unsupported mode: {mode}")

        try:
            if self.platform in ['openai', 'azure']:
                with get_openai_callback() as cb:
                    result = method(query, context, instructions)
                stats = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost": round(cb.total_cost, 4)
                }
            else:
                result = method(query, context, instructions)
                stats = {}
        except:
            result = {
                "question": query,
                "answer": self._err_msg('field'),
                "sources": [],
            }
            stats = {}

        # log the event
        params = {
            "query": query,
            "mode": mode,
            "result": result.copy() if result is not None else None,
            "stats": stats,
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

        # add the event to the result
        result['metadata'] = {
            "timestamp": event['timestamp'],
            "duration": event['duration'],
        }

        return result

    def process_spec_queries(self, spec):
        """
        take a spec containing questions and answer them
        against the docset indexed by the agent
        """

        # retry answers
        retry_answers = ["im having trouble understanding try another way of wording your query",
                         "unknown"]

        # get the list of queries
        query_set = spec.get("query_set", [])
        indx_query_set = {}

        # begin an empty dict
        extracted_info = {}
        query_answers = {}
        grounding = {}

        # foreach query to process
        for one_query in query_set:

            step_answers = {}

            enable = one_query.get("enable", True)
            q_name = one_query['name']

            # make note of this one_query in the index
            # we'll need this later when re-ordering
            indx_query_set[q_name] = one_query

            self.logger.debug(f"Running query: {q_name}",
                                 extra={
                                     'source': self.agent_name,
                                     'data': json.dumps(one_query, indent=4, cls=SafeEncoder)
                                 })

            if not enable:
                continue

            # get the set of steps for this query
            steps = one_query.get("steps", [])

            # for each step
            for one_step in steps:

                # per query vars
                step_name = one_step['name']
                query_mode = one_step.get("mode", "internal")
                query = one_step.get("query")
                context = one_step.get("context", "")
                instructions = one_step.get("instructions", "")
                query_alts = one_step.get("query_alts", [])
                use_alts = one_step.get("use_alts", "on-fail")
                depends = one_step.get("depends", {})
                postprocess = one_step.get("postprocess", {})

                if not query:
                    continue

                # post-processing handling
                pp_handler = postprocess.get("handler")
                pp_response = postprocess.get("response", "fill")
                pp_othercols = postprocess.get("othercols", [])

                # collect all the queries we need to run
                queries = [query] + query_alts

                # do any query modifications
                params = {}
                stop_steps = False
                for p in depends.get("steps", []):
                    a = step_answers.get(p, "")
                    if len(a) == 0:
                        stop_steps = True
                    params[p] = a
                for p in depends.get("queries", []):
                    a = query_answers.get(p, "")
                    if len(a) == 0:
                        stop_steps = True
                    params[p] = a
                if stop_steps:
                    break
                # var substition for the queries
                queries = [q.format(**params) for q in queries]
                # var substition for the instructions
                instructions = instructions.format(**params)
                # var substition for the context
                context = context.format(**params)

                # run the queries against the LLM
                for q_cnt, query in enumerate(queries):

                    print (f"--> {q_name}:{step_name}:Q{q_cnt}")
                    # print (f"{q_name}: {query} {instructions}")

                    # get the answer
                    response = self.query(query, context, instructions, mode=query_mode)
                    answer = response['answer']
                    sources = response.get('sources', [])
                    # normalized answer
                    s_answer = answer.translate(str.maketrans('', '', string.punctuation)).lower().strip()

                    # check the answer for UNKNOWN
                    # but only in the case when postprocess->response==fill
                    # this is for correct handling of spec extension/replacement
                    if pp_response == 'fill':
                        if s_answer in retry_answers:
                            continue

                    # post-process if needed
                    # check if handler is callable
                    if callable(pp_handler):
                        # collect all the columns needed to post-process the answer
                        params = {q_name: answer}
                        for col in pp_othercols:
                            if col in extracted_info:
                                if isinstance(extracted_info[col], list):
                                    val = extracted_info[col][0]
                                else:
                                    val = extracted_info[col]
                                params[col] = val
                        answer = pp_handler(params)

                    # note the answer
                    # we may need it for subs in later queries
                    step_answers[step_name] = answer
                    query_answers[q_name] = answer
                    print(answer)

                    # if next step action is 'extend'
                    # then, we need to extend the query spec
                    if pp_response == "extend":
                        query_set.extend(answer)
                        # continue, so that we move to the next query
                        continue

                    # if next step action is 'replace'
                    # then, we need to replace the query_set items in the default query spec
                    # with the newly loaded one
                    if pp_response == "replace":
                        # get the names of all query items in replace spec
                        replace_query_set_items = {}
                        for q_item in answer:
                            replace_query_set_items[q_item['name']] = q_item
                        # now, run through each query item in the default query set
                        # and check if replacement is needed
                        for i in range(len(query_set)):
                            if query_set[i]['name'] in replace_query_set_items:
                                # we have found a query item that needs to be replaced
                                query_set[i] = replace_query_set_items[query_set[i]['name']]

                        # continue, so that we move to the next query
                        continue

                    # add the answers to the columns in the extracted dataset
                    ans = extracted_info.get(q_name,[])
                    if answer in ans:
                        # we have found this answer before
                        # no need to collect it again
                        continue
                    ans.append(answer)
                    extracted_info[q_name] = ans

                    # at this point, at least one alt query has response
                    # collect the grounding elements
                    if len(sources) > 0:
                        curr_sources = grounding.get(q_name, [])
                        curr_sources.append(sources)
                        grounding[q_name] = curr_sources

                    # check if we need to run other alts
                    if use_alts == "on-fail":
                        # no need to run an alt query
                        # since we have atleast some response
                        break


        # get the order of fields to return
        reordered_query_set = []
        queryset_order = spec.get("order")
        if not queryset_order:
            # we don't have an explicit order provided
            # use the default ordering
            reordered_query_set = query_set
        else:
            for qso in queryset_order:
                if qso in indx_query_set:
                    one_query = indx_query_set[qso]
                    reordered_query_set.append(one_query)

        # check if all columns exist
        # and add the collected grounding
        extracts = {}
        for one_query in reordered_query_set:
            # check if we need to inlcude this field
            enable = one_query.get("enable", True)
            if not enable:
                continue
            include = one_query.get("include", True)
            if not include:
                continue

            # we need to include this field
            q_name = one_query['name']
            q_title = one_query.get("title", q_name)
            default = one_query.get("default")
            default = [[]] if default == None else [default]
            extracts[q_name] = {
                "title": q_title,
                "n_steps": 0 if not extracted_info.get(q_name) else len(extracted_info[q_name]),
                "steps": extracted_info.get(q_name),
                "answer": extracted_info.get(q_name, default)[-1],
                "sources": grounding.get(q_name, []),
            }

        return extracts

    def process_spec_signatures(self, spec):
        """
        check if signatures are present
        """
        self.logger.debug("Detecting signatures...",
                             extra={'source': self.agent_name})

        if spec.get("detect_signatures", False) == False:
            return None

        pages = []
        confidence = 0
        if len(self.doc_signatures) > 0:
            for signature in self.doc_signatures:
                pages.append(signature['page'])
                confidence += signature['confidence']
            n_sigs = len(pages) # this is correct
            pages = list(set(pages))
            n_pages = len(pages)
            confidence = round(confidence/n_sigs, 2)

            comment = f"Detected {n_sigs} signatures across {n_pages} pages"

            signatures = {
                "found": True,
                "comment": comment,
                "n_signatures": n_sigs,
                "n_pages": n_pages,
                "pages": pages,
                "confidence": confidence,
            }
        else:
            signatures = {
                "found": False,
                "comment": f"No signatures detected",
            }

        return signatures

    def process_spec(self, spec):
        """
        process a profilespec
        """
        name = spec.get("name")
        self.logger.debug(f"Processing spec: {name}",
                             extra={
                                 'source': self.agent_name,
                                 'data': json.dumps(spec, indent=4, cls=SafeEncoder)
                             })

        # check for signatures
        signatures = self.process_spec_signatures(spec)

        # process the questions
        extracts = self.process_spec_queries(spec)

        result = {
            "spec": name,
            "timestamp": time.time(),
            "extracts": extracts,
            "signatures": signatures
        }

        return result

    def extracts_to_df(self, info):
        """
        Convert extracts object into dataframe
        """
        extracts = info['extracts']
        entries = []

        for col, details in extracts.items():

            sources = []
            if len(details['sources'])>0:
                for sourceset in details['sources']:
                    for source in [sourceset[0]]:
                        sources.append(source['content'])

            steps = []
            steps = [] if not isinstance(details['steps'], list) else details['steps']

            entry = {
                "field": col,
                "title": details['title'],
                "answer": details['answer'],
                "grounding": "\n\n".join(sources),
                "n_steps": details['n_steps'],
                "steps": "\n".join(steps),
            }
            entries.append(entry)

        df = pd.DataFrame(entries)

        return df


################### BEGIN TESTBED ###################

if __name__ == "__main__":

    # vars
    # cred = get_credentials_by_name('openai-api')
    persist_directory = "chromadb123"
    path = '...'

    agentname = "test_agent"
    # profilespec = get_profilespec()
    print(json.dumps(profilespec, indent=4, cls=SafeEncoder))
    platform = "azure"

    # create an agent
    agent = LLMMultiStepAgent(name=agentname, platform=platform)

    # load the data
    data = agent.load_data(content=path)

    # add to index
    agent.create_add_index(data=data,
                           store="chroma",
                           persist_directory=persist_directory,
                           index_name=agentname)

    # run the profilespec of queries
    info = agent.process_spec(profilespec)

    # output extraction
    for field, extract in info.get("extracts", {}).items():
        print (f"{field}: {extract.get('answer')}")
