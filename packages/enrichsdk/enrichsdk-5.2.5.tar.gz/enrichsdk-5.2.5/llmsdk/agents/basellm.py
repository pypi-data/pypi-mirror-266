import os
import json
import time
import codecs
import pickle
import hashlib
import logging
from logging.config import dictConfig

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.utilities import SerpAPIWrapper
from langchain.schema import ChatMessage
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import PDFMinerLoader
# from langchain.document_loaders import PyPDFium2Loader
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import DirectoryLoader

import chromadb
from chromadb.config import Settings

import fitz

from llmsdk.agents import agent_events
from llmsdk.lib.statemgmt import RedisMixin

try:
    from llmsdk.services.log import *
    logging.config.dictConfig(log_config)
except:
    logging.basicConfig()

class BaseLLMAgent(RedisMixin):
    """
    Class to define the base Hasper LLM agent
    """

    def __init__(self,
                 name,
                 cred,
                 agent_type,
                 platform="openai",
                 searchapi="serpapi",
                 statestore="redis",
                 memory_size=1000,
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

        # logging
        self.logger = get_logger()

        # name
        start_time = time.time()
        self.agent_name = name
        self.agent_type = agent_type
        self.agent_id = self._create_id(f"{self.agent_name}_{start_time}")

        # How many documents/chunks to respond to?
        self.topk = topk

        # statekey of the agent
        # the statekey is a pointer to the current state of the agent
        # this state can be persisted to some store
        # when needed, any previous persisted state
        # can be recalled and reassigned to the agent
        # for now, statekey is static
        # in the future, we can store and retrieve possibly multiple states
        self.statekey = f"sk:{self.agent_type}#{self.agent_name}"

        # creds
        self.cred = cred

        # LLM params
        self.platform = platform

        # init the llm and embeddings objects
        self.llm, self.embeddings = self._get_llm_objs(platform=self.platform,
                                                       cred=self.cred)


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
            "agent_id": self.agent_id,
            "timestamp": round(ts, 3),
            "duration": round(duration, 3),
            "name": event_name,
            "params": params,
        }
        self.metadata['events'].append(event)

        # log the event
        self.logger.debug(event_name,
                             extra={
                                 'source': self.agent_name,
                                 'data': json.dumps(event, indent=4)
                             })


        return event

    def _get_llm_objs(self, platform, cred):
        # get the api key from creds
        api_key = self._get_api_key(cred, platform)

        # init the LLM
        if platform == "openai":

            # get the llm object
            # gpt-3.5-turbo
            llm = ChatOpenAI(temperature=0,
                             model="gpt-3.5-turbo",
                             openai_api_key=api_key,
                             request_timeout=20)

            # get the embeddings object
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)

        elif platform == "azure":

            api_type = 'azure'
            api_version = '2023-05-15' # this may change in the future

            # get the llm object
            # based on deployment
            api_key = os.getenv("AZURE_OPENAI_KEY")
            api_base = os.getenv("AZURE_OPENAI_ENDPOINT") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_GPT") # this will correspond to the custom name you chose for your deployment when you deployed a model
            llm = AzureChatOpenAI(openai_api_base=api_base,
                                  openai_api_version=api_version,
                                  deployment_name=deployment_name,
                                  openai_api_key=api_key,
                                  openai_api_type=api_type,
                                  temperature=0,
                                  request_timeout=20)

            # get the embeddings object
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_API_TYPE"] = api_type
            os.environ["OPENAI_API_BASE"] = api_base
            os.environ["OPENAI_API_VERSION"] = api_version
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_EMBEDDING") # this will correspond to the custom name you chose for your deployment when you deployed a model
            embeddings = OpenAIEmbeddings(deployment=deployment_name,
                                          model="text-embedding-ada-002",
                                          chunk_size=16)

        else:
            llm = None
            embeddings = None

        return llm, embeddings

    def _load_search_agent(self, cred, searchapi, llm):
        """
        setup the search agent
        this agent will be used to run searches against search engines
        useful to get realtime answers to queries
        """
        # get the api key from creds
        api_key = self._get_api_key(cred, searchapi)

        # setup the search tool
        if searchapi == "serpapi":
            searchengine = SerpAPIWrapper(serpapi_api_key=api_key)
        else:
            searchengine = None
        if searchengine == None:
            return None

        tools = [
            Tool(
                name="Search",
                func=searchengine.run,
                description="Useful for when you need to answer questions about current events. Do not try to click on links. Input must be a search query."
            )
        ]
        # create the agent
        agent_chain = initialize_agent(tools,
                                       llm,
                                       agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                       verbose=False)
        return agent_chain, searchengine

    def _get_path_source(self, fpath):
        """
        infer the format from the content path name
        """
        if os.path.isdir(fpath):
            return "dir"
        else:
            return fpath.split('.')[-1]

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


    ##
    ## interfaces
    ##

    def get_metadata(self):
        """
        return metadata collected by the agent
        """
        return self.metadata


    ## state management

    def get_statekey(self):
        """
        return the statekey which points to the
        latest state of the agent
        """
        return self.statekey

    def clear_agent_state(self):
        """
        clear the memory context of the agent
        this is useful when we want to agent to
        start off a new QnA session
        """
        start_time = time.time()

        # clear the memories
        self.memory.clear()
        self.kg.clear()

        # reset the context and KG vars
        self.latest_context = []
        self.current_kg = []

        # make note of the clear action
        duration = time.time() - start_time
        params = {}
        event = self._log_event(agent_events._EVNT_STATECLEAR, duration, params=params)

        return

    def get_agent_state(self):
        """
        get the state of the agent
        """
        # get the memories
        memory = self.memory
        kg = self.kg

        # get the context and KG vars
        latest_context = self.latest_context
        current_kg = self.current_kg

        # setup the state object
        state = {
            "memory": memory,
            "kg": kg,
            "latest_context": latest_context,
            "current_kg": current_kg,
        }

        return state

    def store_agent_state(self):
        """
        store the agent state in some external storage
        this is useful when we want to later retrieve
        the state and re-animate an agent with the retrieved state
        """
        start_time = time.time()

        # get the state
        state = self.get_agent_state()

        # pickle it for transport
        state_pkl = codecs.encode(pickle.dumps(state), "base64").decode()

        # store it
        success = False
        statekey = self.statekey
        if self.state_store == "redis":
            cred = self.cred.get(self.state_store, {})
            success = self.store_state_redis(statekey, state_pkl, cred)
        elif self.state_store == "db":
            pass
        elif self.state_store == "disk":
            pass
        else:
            raise Exception(f"Unknown state store for agent, cannot store the agent's state for {statekey}")

        # make note of the action
        if success:
            duration = time.time() - start_time
            params = {
                "statekey": statekey,
                "store": self.state_store
            }
            event = self._log_event(agent_events._EVNT_STATESTORE, duration, params=params)

        return success

    def set_agent_state(self, statekey):
        """
        get a previously stored state
        and re-animate the agent with it
        """
        start_time = time.time()
        success = False

        # retrieve the state from storage
        state_pkl = None
        if self.state_store == "redis":
            cred = self.cred.get(self.state_store, {})
            state_pkl = self.retrieve_state_redis(statekey, cred)
        elif self.state_store == "db":
            pass
        elif self.state_store == "disk":
            pass
        else:
            raise Exception(f"Unknown state store for agent, cannot retrieve state for {statekey}")

        state = None
        if state_pkl:
            # re-animate our agent with the retrieved state
            # unpickle the state pickle
            try:
                state = pickle.loads(codecs.decode(state_pkl.encode(), "base64"))
            except:
                self.logger.error("Cannot re-animate agent with retrieved state, setting clear state",
                                     extra={
                                         'source': self.agent_name,
                                         'data': f"State pickle: {state_pkl}"
                                     })
                # clear the agent state
                self.clear_agent_state()

        if state:
            # re-hydrate state vars
            if state.get('memory'):
                self.memory = state['memory']
            if state.get('kg'):
                self.kg = state['kg']
            if state.get('latest_context'):
                self.latest_context = state['latest_context']
            if state.get('current_kg'):
                self.current_kg = state['current_kg']
            success = True

        # note the action
        duration = time.time() - start_time
        params = {
            "statekey": statekey,
            "success": success,
            "store": self.state_store
        }
        event = self._log_event(agent_events._EVNT_STATERESTORE, duration, params=params)

        return


    ## data loading

    def chunk_data(self, data, _format):
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
                content = data[i].page_content

                # add bboxes for pdf docs
                if _format == "pdf":
                    pageno = data[i].metadata['page']
                    page = self.docs[source].load_page(pageno)
                    instances = page.search_for(content)
                    bboxes = []
                    for inst in instances:
                        bboxes.append([inst.x0, inst.y0,
                                       inst.x1, inst.y1])
                    data[i].metadata['bboxes'] = json.dumps(bboxes)

                # add other metadata
                data[i].metadata['file'] = source.split('/')[-1]
                if curr_source != source:
                    curr_source = source
                    chunk = 1
                data[i].metadata['chunk'] = chunk
                if _format == "str":
                    data[i].metadata['id'] = self._create_id(f"{source}-{self._create_id(content)}-{chunk}")
                else:
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

    def load_data(self, content, source=None, metadata={}, params={}):
        """
        set the datasource loader, loads and cleans the data
        content: data content (path, text) depending on type of source
        source:
            'dir' points to a folder with one or more files to load
            'pdf' points to a single PDF file to load
            'str' contains a text string to load
            None will try to infer automatically
        params: extra params needed for specific loaders
                    glob: what glob filter to use if source=='dir'
                    pdfloader: what type of pdf loader module to use if source=='pdf'
        metadata: any custom metadata to pass when source=='str'
        """

        start_time = time.time()
        success = False

        if not source:
            source = self._get_path_source(content)

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

            # make note of this document
            # we'll need to access it later for metadata
            if data:
                self.docs[content] = fitz.open(content)

        elif source == 'docx':
            loader = Docx2txtLoader(content)
            data = loader.load()

        elif source == 'str':
            # special handling for string inputs
            metadata['source'] = source
            data = [Document(page_content=content, metadata=metadata)]

        else:
            data = None

        # chunk the data
        if data:
            data = self.chunk_data(data, source)
            success = True

        # log that the data loader is ready
        duration = time.time() - start_time
        params = {
            "success": success,
            "source": source,
            "content": content,
            "params": params,
            "metadata": metadata,
        }
        event = self._log_event(agent_events._EVNT_DATA, duration, params=params)

        return data


    ## index management

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
            if self.index_store == 'chroma':
                self.add_to_index_chroma(data)
                # force topk count to be at max count of index
                self.topk = min(self.topk, self.index.count())
            else:
                raise Exception(f"{self.index_store} does not support adding document")
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
        self.index_store = store
        self.index_name = self.agent_name if not index_name else index_name

        # create the index
        if store == 'faiss':
            self.index = FAISS.from_documents(data, self.embeddings)
        elif store == 'chroma':
            self.index = self.create_add_index_chroma(data, persist_directory=persist_directory)
            # force topk count to be at max count of index
            self.topk = min(self.topk, self.index.count())
        else:
            self.index = None
            self.index_store = None

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
        self.index_store = store

        # load the index
        if self.index_store == 'chroma':
            self.vdb_client = chromadb.Client(Settings(
                                    chroma_db_impl="duckdb+parquet",
                                    persist_directory=persist_directory
                                ))
            self.index_name = index_name
            self.index = self.vdb_client.get_collection(name=self.index_name,
                                                          embedding_function=self.embeddings.embed_documents)
            # force topk count to be at max count of index
            self.topk = min(self.topk, self.index.count())
        else:
            self.index = None

        # log that the index is ready
        duration = time.time() - start_time
        params = {
            "store": self.index_store,
            "persist_directory": persist_directory,
        }
        event = self._log_event(agent_events._EVNT_INDEXLOAD, duration, params=params)

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
                    "store": self.index_store,
                    "n_items": self.index.count()
                }
            except:
                raise Exception("Index does not support stats")
        return stats

    def search_chromadb(self, query, k=7, include_metadata=True):
        """
        run a search against the chromadb index for a list of queries
        """
        # perform query
        results = self.index.query(query_texts=[query],
                                    n_results=k,
                                    where=None,
                                    where_document=None)
        # construct result docset
        docs = []
        for i in range(0, len(results['documents'][0])):
            page_content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            metadata['distance'] = distance
            doc = Document(page_content=page_content, metadata=metadata)
            docs.append(doc)

        return docs

    def _add_docset_chroma(self, index, data):
        """
        populate the index
        """
        if len(data) == 0:
            # cannot add anything
            return

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
        ids = list(set([doc.metadata.get('id') for doc in data]))
        if len(ids) == 1:
            where_clause = {"id": ids[0]}
        else:
            where_clause = {
                "$or": [{"id": _id} for _id in ids]
            }
        index.delete(
            where=where_clause
        )
        return


    ## document search

    def get_similar_docs(self, query, topk=7):
        """
        get top-K similar docs from an index given a query
        query: query string
        index: index object
        topk: number of top-K similar docs to matching query to return
        """

        if self.index:
            if self.index_store == 'faiss':
                docs = self.index.similarity_search(query,
                                                    k=topk,
                                                    include_metadata=True)
            elif self.index_store == 'chroma':
                docs = self.search_chromadb(query,
                                            k=topk,
                                            include_metadata=True)
            else:
                docs = None

        return docs
