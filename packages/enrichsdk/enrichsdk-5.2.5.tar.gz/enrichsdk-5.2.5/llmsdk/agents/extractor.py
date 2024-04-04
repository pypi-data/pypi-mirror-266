import json
import time
import string
from re import sub

from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback

from . import agent_events
from llmsdk.agents.basellm import BaseLLMAgent
from ..lib import extractors
from llmsdk.lib import SafeEncoder

__all__ = ['LLMQuerierExtractor']

class LLMQuerierExtractor(BaseLLMAgent):
    """
    Class to do querying of a docset and extracting specific information fields using LLMs
    Query can be run against a specified set of documents that act
    as context to constrain the answers
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
                         agent_type="extract",
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

        # init the QnA chain for internal queries
        prompt = self._get_query_prompt_internal()
        self.llm_chain_int = load_qa_chain(llm=self.llm,
                                           chain_type=self.chaintype,
                                           prompt=prompt)
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

    def _get_query_prompt_internal(self):
        """
        generate a prompt for running a query in internal mode
        """
        template = """You are a highly advanced AI program designed to extract specific pieces of information from business documents.
Be precise in the responses you provide. Do not respond in full sentences, but only with the specific information asked for.
You will be provided with relevant pieces of context extracted from a business document to answer the question at the end.
If the question asks you to format your answer in some specific manner, do so.
If the question includes instructions to help you with extraction, follow those instructions.
If you cannot find the answer in the context, just say 'unknown', don't try to make up an answer and do not provide any explanations.

------ BEGIN CONTEXT ------
{context}
------ END CONTEXT ------

------ BEGIN QUESTION ------
{input} {instructions}
------ END QUESTION ------

Your response:"""

        prompt = PromptTemplate(
            input_variables=["input", "context", "instructions"],
            template=template
        )

        return prompt

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

    def run_query_search(self, query, instructions=""):
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

    def run_query_internal(self, query, instructions=""):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # get the similar docs
        docs = self.get_similar_docs(query, topk=self.topk)

        # setup the QnA chain object
        response = self.llm_chain_int({"input_documents":docs, "input":query, "instructions":instructions},
                                      return_only_outputs=False)

        # run the query against the similar docs
        result = {
            "question": query,
            "answer": response.get('output_text', self._err_msg('field')).strip(),
            "sources": [{"content": d.page_content, "metadata": d.metadata, "distance": d.metadata.pop('distance')} for d in docs],
        }

        return result

    def query(self, query, instructions="", mode="internal"):
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
                    result = method(query, instructions)
                stats = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_cost": round(cb.total_cost, 4)
                }
            else:
                result = method(query, instructions)
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
        grounding = {}

        # foreach query to process
        for one_query in query_set:

            enable = one_query.get("enable", True)
            q_name = one_query['name']
            query = one_query.get("query")
            query_mod = one_query.get("query_mod")
            query_alts = one_query.get("query_alts", [])
            use_alts = one_query.get("use_alts", "on-fail")
            postprocess = one_query.get("postprocess", {})
            fill_columns = one_query.get("fill_columns", [])
            query_mode = one_query.get("mode", "internal")
            instructions = one_query.get("instructions", "")

            # post-processing handling
            pp_handler = postprocess.get("handler")
            pp_response = postprocess.get("response", "fill")
            pp_othercols = postprocess.get("othercols", [])

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

            if not query:
                continue

            if query_mod:
                # we have to modify our query before passing to the LLM
                cannot_modify = False
                params = {}
                for col in query_mod.get("inputs", []):
                    if col not in extracted_info:
                        cannot_modify = True
                        break
                    else:
                        params[col] = extracted_info[col]
                if cannot_modify:
                    continue

                # modify the query using the params collected
                query = query.format(**params)

                # check if we need to modify alt queries also
                apply_to = query_mod.get("apply_to", "first")
                if apply_to == "all":
                    query_alts = [q.format(**params) for q in query_alts]

            # collect all the queries we need to run
            queries = [query] + query_alts

            # run the queries against the LLM
            for query in queries:

                # get the answer
                response = self.query(query, instructions=instructions, mode=query_mode)
                answer = response['answer']
                sources = response['sources']
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
                            # remove the found query item from the replace set
                            d = replace_query_set_items.pop(query_set[i]['name'])

                    # now, all the remaining query items need to be incluced
                    for qr_name, q_item in replace_query_set_items.items():
                        query_set.append(q_item)

                    # continue, so that we move to the next query
                    continue

                # add the answers to the columns in the extracted dataset
                if len(fill_columns) == 0:
                    break
                if len(fill_columns) > 1:
                    i = 0
                    for col in fill_columns:
                        ans_i = answer[i]
                        ans = extracted_info.get(col,[])
                        if answer in ans:
                            # we have found this answer before
                            # no need to collect it again
                            continue
                        ans.append(ans_i)
                        extracted_info[col] = ans
                        i += 1
                else:
                    col = fill_columns[0] # have only one column to fill
                    ans = extracted_info.get(col,[])
                    if answer in ans:
                        # we have found this answer before
                        # no need to collect it again
                        continue
                    ans.append(answer)
                    extracted_info[col] = ans

                # at this point, at least one alt query has response
                # collect the grounding elements
                for col in fill_columns:
                    curr_sources = grounding.get(col, [])
                    curr_sources.append(sources)
                    grounding[col] = curr_sources

                # check if we need to run other alts
                if use_alts == "on-fail":
                    # no need to run an alt query
                    # since we have atleast some response
                    break

        # get the order of fields to return
        reordered_query_set = []
        field_order = spec.get("order")
        if not field_order:
            # we don't have an explicit order provided
            # use the default ordering
            reordered_query_set = query_set
        else:
            for field in field_order:
                if field in indx_query_set:
                    one_query = indx_query_set[field]
                    reordered_query_set.append(one_query)

        # check if all columns exist
        # and add the collected grounding
        extracts = {}
        for one_query in reordered_query_set:
            # check if we need to inlcude this field
            include = one_query.get("include", True)
            if not include:
                continue

            # we need to include this field
            fill_columns = one_query.get("fill_columns", [])
            default = one_query.get("default")
            default = [] if default == None else [default]
            for col in fill_columns:
                answer = extracted_info.get(col, default)
                extracts[col] = {
                    "n_answers": len(answer),
                    "answer": answer,
                    "sources": grounding.get(col, []),
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
            entry = {
                "field": col,
                "answer": details['answer'],
                "grounding": json.dumps(details['sources']),
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
    agent = LLMQuerierExtractor(name=agentname, platform=platform)

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
