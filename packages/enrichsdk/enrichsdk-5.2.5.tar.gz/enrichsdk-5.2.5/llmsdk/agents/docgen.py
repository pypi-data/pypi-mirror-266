import os
import time
import json
import hashlib
from collections import defaultdict

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain import PromptTemplate
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationTokenBufferMemory, ConversationKGMemory
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import PDFMinerLoader
# from langchain.document_loaders import PyPDFium2Loader

import chromadb
from chromadb.config import Settings

from . import agent_events

__all__ = ['LLMDocGenerator']

class LLMDocGenerator(object):
    """
    Class to generate text documents using LLMs
    A set of documents that act as context
    against which the agent has to generate text
    """

    def __init__(self,
                 name,
                 cred={},
                 model="openai",
                 searchapi="serpapi"):
        """
        init the LLM query agent
        name: name of the agent
        cred: credentials object
        model: name of the model backend to use
                default to OpenAI GPT model for now
                will be extended in the future to suuport other models
        searchapi: name of the search API backend to use
                    default to serpapi for now
        """

        start_time = time.time()

        # defaults
        self.chunk_size = 1000
        self.chunk_overlap = 100
        self.latest_context = []
        self.context_topK = 1
        self.current_kg = []
        self.metadata = {}
        self.index = None
        self.vdb_client = None
        self.index_name = None
        self.store = None

        # name
        self.agent_name = name

        # creds
        self.cred = cred
        # LLM params
        self.model = model
        self.searchapi = searchapi
        self.chaintype = "stuff"

        # init the llm and embeddings objects
        self.llm, self.embeddings = self._get_llm_objs(model=self.model,
                                                       cred=self.cred)

        # init the QnA chain for internal queries
        prompt = self._get_query_prompt_answer()
        self.llm_chain = load_qa_chain(self.llm,
                                       chain_type=self.chaintype,
                                       prompt=prompt)

        # note metadata for this agent
        self.metadata = {
            "agent": {
                "name": self.agent_name,
                "model": self.model,
                "searchapi": self.searchapi,
                "chaintype": self.chaintype,
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

    def _get_llm_objs(self, model, cred):
        # get the api key from creds
        api_key = self._get_api_key(cred, model)

        # init the model
        if model == "openai":
            # get the llm object
            llm = OpenAI(temperature=0,
                         max_tokens=512,
                         openai_api_key=api_key,
                         request_timeout=60)
            # get the embeddings object
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        else:
            llm = None
            embeddings = None

        return llm, embeddings

    def _get_query_prompt_answer(self):
        """
        generate a prompt for running a query in internal mode
        """
        template = """You are an assistant to a prolific venture capilatist assessing new startups for feasibility of funding.
You will be given a number of context documents about a startup.
Your task is to use the information in the context documents to answer questions about the startup.
Respond in the manner of writing an investor memo.
If you can't find the answer in the context documents, DO NOT MAKE UP AN ANSWER.

        Here are the context documents:
        {context}

        Question: {question}
        Answer:
        """

        prompt = PromptTemplate(
            input_variables=["question", "context"],
            template=template
        )

        return prompt

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

    def _add_docset_chroma(self, index, data):
        """
        populate the index
        """
        ids = [doc.metadata.get("id", self._create_id(doc.page_content)) for doc in data]
        docs = [doc.page_content for doc in data]
        metas = [doc.metadata for doc in data]
        index.add(
            documents=docs,
            metadatas=metas,
            ids=ids)
        return

    def _delete_docset_chroma(self, index, data):
        """
        delete from the index where source matches incoming data
        """
        sources = list(set([doc.metadata.get('source') for doc in data]))
        if len(sources) == 1:
            where_clause = {"source": sources[0]}
        else:
            where_clause = {
                "$or": [{"source": source} for source in sources]
            }
        index.delete(
            where=where_clause
        )
        return


    ## interfaces

    def validate_spec(self, spec):

        if isinstance(spec, dict):
            reqd_keys = ['sections']
            missing = [k for k in reqd_keys if k not in spec]
            if len(missing)>0:
                raise Exception("Invalid specification")
        return

    def load_spec(self, profilespec):
        """
        load the spec for generating the document
        profilespec: path to spec file
        """
        # check path
        if isinstance(profilespec, dict):
            self.validate_spec(profilespec)
            return profilespec

        if os.path.exists(profilespec) and profilespec.endswith(".json"):
            with open(profilespec, "r") as fd:
                spec = json.load(fd)
                self.validate_spec(spec)
                return spec

        return None


    def get_metadata(self):
        """
        return metadata collected by the agent
        """
        return self.metadata

    def chunk_data(self, data):
        """
        create chunks from the data
        and add any needed metadata
        """

        def cleanup_metadata(data):
            # take in a list of data document objects
            # and clean up metadata
            curr_source = None
            for i in range(0, len(data)):
                source = data[i].metadata['source']
                data[i].metadata['file'] = source.split('/')[-1]
                if curr_source != source:
                    curr_source = source
                    chunk = 1
                data[i].metadata['chunk'] = chunk
                data[i].metadata['id'] = self._create_id(f"{source}-{chunk}")
                chunk += 1

                ##
                ## add any other custom metadata here
                ##

            return data

        # chunk the data
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                       chunk_overlap=self.chunk_overlap)
        chunks = text_splitter.split_documents(data)

        # add metadata
        chunks = cleanup_metadata(chunks)

        return chunks

    def load_data(self, source, content, metadata={}, params={}):
        """
        set the datasource loader, loads and cleans the data
        source:
            'dir' points to a folder with one or more files to load
            'pdf' points to a single PDF file to load
            'str' contains a text string to load
        content: data content (path, text) depending on type of source
        params: extra params needed for specific loaders
                    glob: what glob filter to use if source=='dir'
                    pdfloader: what type of pdf loader module to use if source=='pdf'
        metadata: any custom metadata to pass when source=='str'
        """

        start_time = time.time()

        if source == 'dir':
            glob = params.get("glob", "**/*.*")
            loader = DirectoryLoader(content, glob=glob, recursive=True)
            data = loader.load()

        elif source == 'pdf':
            pdfloader = params.get("pdfloader", "pymupdf")
            if pdfloader == "pymupdf":
                loader = PyMuPDFLoader(content)
                data = loader.load()
            elif pdfloader == "pypdf":
                loader = PyPDFLoader(content)
                data = loader.load_and_split()
            elif pdfloader == "pypdfium2":
                loader = PyPDFium2Loader(content)
                data = loader.load()
            elif pdfloader == "pdfminer":
                loader = PDFMinerLoader(content)
                data = loader.load()
            else:
                data = None

        elif source == 'str':
            # special handling for string inputs
            metadata["source"] = source
            data = [Document(page_content=content, metadata=metadata)]

        else:
            data = None

        # chunk the data
        data = self.chunk_data(data)

        # log that the data loader is ready
        duration = time.time() - start_time
        params = {
            "source": source,
            "content": content,
            "params": params,
            "metadata": metadata,
        }
        event = self._log_event(agent_events._EVNT_DATA, duration, params=params)

        return data

    def get_index(self):
        """
        return the index object
        """
        return self.index

    def create_add_index_chroma(self, data, persist_directory=None):
        """
        Init the chromadb index and populate it with a set of documents
        """
        # init the ChromaDB client
        self.vdb_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory # Optional, defaults to .chromadb/ in the current directory
        ))

        # make sure we're starting with a fresh db and collection
        self.vdb_client.reset()
        index = self.vdb_client.get_or_create_collection(name=self.index_name,
                                                         embedding_function=self.embeddings.embed_documents)

        # populate the collection
        self._add_docset_chroma(index, data)

        # persist the index to disk
        if persist_directory:
            self.vdb_client.persist()

        return index

    def add_to_index_chroma(self, data):
        """
        add document(s) to a chromadb index
        """
        # first, delete all existing docs from the same sources
        # as what we are adding, we don't want duplicates
        self._delete_docset_chroma(self.index, data)

        # now, add the new docs
        self._add_docset_chroma(self.index, data)

        # persist the db to disk
        self.vdb_client.persist()

        return

    def add_to_index(self, data):
        """
        add document(s) to the agent's index
        """
        start_time = time.time()

        if self.index:
            if self.store == 'chroma':
                self.add_to_index_chroma(data)
            else:
                raise Exception(f"{self.store} does not support adding document")
        else:
            raise Exception("No available index, cannot add document")

        # log that the doc is added
        if self.index:
            duration = time.time() - start_time
            params = {
                "n_items": len(data),
            }
            event = self._log_event(agent_events._EVNT_INDEXADD, duration, params=params)

        return

    def create_add_index(self, data, store='chroma', persist_directory=None, index_name=None):
        """
        create an index from a data source
        data: list of langchain Document() objects
        store: type of vectorstore to use (chroma, faiss, ...)
        """

        start_time = time.time()

        # note what store we are using and the index name
        self.store = store
        self.index_name = self.agent_name if not index_name else index_name

        # create the index
        if store == 'faiss':
            self.index = FAISS.from_documents(data, self.embeddings)
        elif store == 'chroma':
            self.index = self.create_add_index_chroma(data, persist_directory=persist_directory)
        else:
            self.index = None
            self.store = None

        # log that the index is ready
        if self.index:
            duration = time.time() - start_time
            params = {
                "store": store,
                "persist_directory": persist_directory,
                "index_name": self.index_name,
                "n_items": len(data)
            }
            event = self._log_event(agent_events._EVNT_INDEXCREATE, duration, params=params)

        return

    def load_index(self, persist_directory, index_name, store='chroma'):
        """
        load an already persisted index from a directory
        persist_directory: location of persisted index
        store: type of vectorstore to use (chroma, ...)
                only supports chroma for now
        """
        start_time = time.time()

        # make note of the store type
        self.store = store

        # load the index
        if self.store == 'chroma':
            self.vdb_client = chromadb.Client(Settings(
                                    chroma_db_impl="duckdb+parquet",
                                    persist_directory=persist_directory
                                ))
            self.index_name = index_name
            index = self.vdb_client.get_collection(name=self.index_name,
                                                  embedding_function=self.embeddings.embed_documents)
        else:
            index = None

        # log that the index is ready
        duration = time.time() - start_time
        params = {
            "store": self.store,
            "persist_directory": persist_directory,
        }
        event = self._log_event(agent_events._EVNT_INDEXLOAD, duration, params=params)

        self.index = index

        return

    def get_index_stats(self):
        """
        return some stats about the agent's index
        """
        stats = None
        if self.index:
            try:
                stats = {
                    "name": self.index_name,
                    "store": self.store,
                    "n_items": self.index.count()
                }
            except:
                raise Exception("Index does not support stats")
        return stats

    def search_chromadb(self, query, k=7, include_metadata=False):
        """
        run a search against the chromadb index for a list of queries
        """
        # perform query
        results = self.index.query(
                    query_texts=[query],
                    n_results=k,
                    where=None,
                    where_document=None)
        # construct result docset
        docs = []
        for i in range(0, len(results['documents'][0])):
            page_content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            doc = Document(page_content=page_content, metadata=metadata)
            docs.append(doc)

        return docs

    def get_similar_docs(self, query, topk=7):
        """
        get top-K similar docs from an index given a query
        query: query string
        index: index object
        topk: number of top-K similar docs to matching query to return
        """
        if self.index:
            if self.store == 'faiss':
                docs = self.index.similarity_search(query,
                                                    k=topk,
                                                    include_metadata=True)
            elif self.store == 'chroma':
                docs = self.search_chromadb(query,
                                            k=topk,
                                            include_metadata=True)
            else:
                docs = None

        return docs

    def generate_query_prompt_kwords(self, context=""):
        """
        generate a prompt for extracting keywords from a paragraph
        """
        template = """You are the chief of staff to a busy executive. You will be given a paragraph of text
        and must identify at most five key phrases from the paragraph. Do not summarize what you find,
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

        return prompt.format(context=context)

    def run_query_kwords(self, context=""):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers that generic llm can provide
        """
        # augment the query with some context to guide the LLM
        query = self.generate_query_prompt_kwords(context)
        result = self.llm(query)
        result = result.strip()
        # a few tries to extract the response
        # sometimes, the LLM messes up
        try:
            result = json.loads(result)
        except:
            try:
                result = json.loads(f"[{result.split('[')[-1]}")
            except:
                pass

        return result

    def generate_query_prompt_collation(self, text, intent, method):
        """
        generate a prompt for summarizing text
        """

        if method == 'summarize':
            template = """Given the following long text (given in backquotes below), summarize it to be {intent}.

            ```
            {text}
            ```

            Summary:
            """
        elif method == 'rewrite':
            template = """Rewrite the following text (given in backquotes below), {intent}, to make it more coherent.

            ```
            {text}
            ```

            Response:
            """
        else:
            template = None

        prompt = PromptTemplate(
            input_variables=["intent", "text"],
            template=template,
        )

        return prompt.format(intent=intent, text=text)

    def run_query_collation(self, intent, text, method):
        """
        run a query using llm to summarize multiple paras of text
        """
        # augment the query with some context to guide the LLM
        prompt = self.generate_query_prompt_collation(text, intent, method)
        result = self.llm(prompt)
        result = result.strip()
        result = {
            "intent": intent,
            "text": text,
            "answer": result,
            "sources": [{"content": text, "source": f"doc-collation-{method}"}]
        }

        return result

    def run_query_answer(self, query):
        """
        run a query using llm on an internal docset indexed in index
        this is useful when looking for answers using a private source of data
        """
        # get the similar docs
        docs = self.get_similar_docs(query)

        # setup the QnA chain object
        response = self.llm_chain({"input_documents":docs, "question":query},
                                    return_only_outputs=True)

        # run the query against the similar docs
        result = {
            "question": query,
            "answer": response.get('output_text', self._err_msg('field')).strip(),
            "sources": [{"content": d.page_content, "source": d.metadata['source']} for d in docs]
        }

        # check if suggest call is needed
        if ('output_text' not in response) or ("i am not sure" in result['answer'].lower()):
            # we don't have a usable answer, so no need for sources
            result['sources'] = []

        return result

    def prompt(self, prompt, mode="answer"):
        """
        run a query on an index using an llm chain object
        prompt: prompt dict containing
            query: when mode=answer
            intent: when mode=summarize
            text: when mode=summarize
        index: index object
        llm: llm object
        mode: 'internal' for querying over docset,
        context: text used to guide the LLM when running in 'external' mode
        """

        start_time = time.time()

        result = None
        if mode == 'answer':
            query = prompt.get('query')
            if query:
                result = self.run_query_answer(query)
        elif mode == 'collate':
            text = prompt.get('text')
            intent = prompt.get('intent', "one para")
            collation = prompt.get('collate', "summarize")
            if text:
                result = self.run_query_collation(intent=intent, text=text, method=collation)
        else:
            pass

        if result:
            answer = result['answer']
            # add keywords identified to the result
            result['keywords'] = self.run_query_kwords(context=answer)

        # log the event
        params = {
            "prompt": prompt,
            "mode": mode,
            "result": result.copy(),
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_QUERY, duration, params=params)

        # add the event to the result
        result['metadata'] = {
            "timestamp": event['timestamp'],
            "duration": event['duration'],
        }

        return result

    def generate_doc(self, profilespec="profilespec.json"):
        """
        generate the document
        """

        start_time = time.time()

        # load the spec first
        self.spec = self.load_spec(profilespec)
        if self.spec is None:
            return None

        # get prefix, suffix
        prefix = self.spec.get('prompt', {}).get('prefix', "")
        suffix = self.spec.get('prompt', {}).get('suffix', "")

        # get sections
        sections = self.spec.get('sections')

        full_text = "-- BEGIN: Investor Memo --" + "\n\n\n"

        for section, detail in sections.items():

            enable = detail.get('enable', True)
            if not enable:
                continue

            # form the section header
            header = detail['title']
            header_text = f'{header}' + "\n" + '_'*len(header) + "\n\n"

            # run through each question for that section
            section_text = ""
            section_sources = []
            section_keywords = []
            for query in detail['questions']:
                # query using the agent
                query = f"{prefix} {query} {suffix}"
                prompt = { "query": query }
                result = self.prompt(prompt, mode="answer")
                answer = result['answer']
                sources = result['sources']
                keywords = result['keywords']
                section_sources += [source['source'] for source in sources]
                section_keywords += keywords

                # form the answer for this question
                section_text += f'{answer}' + "\n\n"

            # summarize the section if needed
            collate = detail.get('collate')
            if collate:
                intent = detail.get('intent', detail.get('title'))
                prompt = {
                    "text": section_text,
                    "intent": intent,
                    "collate": collate,
                }
                result = self.prompt(prompt, mode="collate")
                section_text = result['answer']
                section_text += "\n\n"
                section_keywords = result['keywords']

            # add the keywords for this section
            section_keywords = list(set(section_keywords))
            section_text += "Keywords: " + ", ".join(section_keywords) + "\n\n"

            # add the sources for this section
            section_sources = list(set(section_sources))
            section_text += "Sources: " + ", ".join(section_sources) + "\n\n\n"

            # create the section text for this section
            full_text += f'{header_text}{section_text}'

        full_text += "\n-- Investor Memo :END --"

        # log the event
        params = {
            "spec": self.spec
        }
        duration = time.time() - start_time
        event = self._log_event(agent_events._EVNT_DOCGEN, duration, params=params)

        return full_text

def get_sample_profilespec():

    return {
	    "prompt": {
		    "prefix": "write a para about",
		    "suffix": "for this startup company"
	    },
	    "sections": {
		    "about": {
			    "enable": True,
			    "title": "About the Company",
			    "intent": "introducing the startup",
			    "questions": [
				    "industry and specific focus",
				    "key technologies developed",
				    "unique value proposition"
			    ],
			    "collate": False,
		    },
		    "founders": {
			    "enable": True,
			    "title": "Company Founders",
			    "intent": "about the co-founders of the startup",
			    "questions": [
				    "co-founders and the roles they hold",
				    "past experience of co-founders"
			    ],
			    "collate": "rewrite"
		    },
		    "market-analysis": {
			    "enable": True,
			    "title": "Market Analysis",
			    "intent": "about market analysis for this startup",
			    "questions": [
				    "target customer base",
				    "other potential customers",
				    "other comparable companies and startups in this space",
				    "the main competitors",
				    "biggest risk factors",
				    "key differentiators",
				    "market trends for the domain"
			    ],
			    "collate": False
		    }
	    }
    }

if __name__ == "__main__":

    # vars
    dirpath = os.path.expandvars("$DATA_ROOT/$AGENTNAME/acme_1/bulk")
    singlepdf = os.path.expandvars("$DATA_ROOT/$AGENTNAME/acme_1/single/spotlight.pdf")
    persist_directory = os.path.expandvars("$DATA_ROOT/$AGENTNAME/acme_1/chromadb_index")
    index_name = "acme_1_index"
    profilespec = get_sample_profilespec()
    outfile = None # /path/to/generated/document

    #cred = get_credentials_by_name('openai-api')
    cred = None # environment variable...

    # we'll first create one agent
    # point it to a folder with multiple files to create an index
    # then add one more file to the index in a separate step

    # create the docgen agent
    agent = LLMDocGenerator(name="agent_acme_1",
                            cred=cred)

    # point it to the folder containing multiple pdfs
    data = agent.load_data(source="dir",
                            content=dirpath,
                            params={"glob":"**/*.pdf"})
    # create the index atop the data
    agent.create_add_index(data=data,
                            store="chroma",
                            persist_directory=persist_directory,
                            index_name=index_name)
    # check index stats
    print (json.dumps(agent.get_index_stats(), indent=4))

    # now, add one more pdf using the PyMuPDF loader
    data = agent.load_data(source="pdf",
                            content=singlepdf,
                            params={"pdfloader":"pymupdf"})
    # check index stats again
    print (json.dumps(agent.get_index_stats(), indent=4))
    # we now have the index populated with all the data we need

    # we can run the document generation step with this agent
    # or we can create another agent, point it to the index we created
    # and use that agent to generate the document
    # let's do the latter

    # create a new docgen agent
    agent2 = LLMDocGenerator(name="agent_acme_2")
    # point it to the index we created earlier
    # use the same index name
    agent2.load_index(persist_directory=persist_directory,
                        index_name=index_name,
                        store="chroma")
    # check index stats, it should match what the first agent has
    print (json.dumps(agent2.get_index_stats(), indent=4))

    # use the second agent to generate the document and save
    profilespec = get_sample_profilespec()
    full_text = agent2.generate_doc(profilespec=profilespec)
    if outfile is None:
        print(full_text)
    else:
        with open(outfile, "w") as fd:
            fd.write(full_text)
        print(f"Output in {outfile}")
