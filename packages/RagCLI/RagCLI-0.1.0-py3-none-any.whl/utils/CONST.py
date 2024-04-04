__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import logging

# Diverse Consts
NULLSTRING = ""
ENCODING = "utf-8"

# Logger configuration
TRACE_DEFAULT_LEVEL = logging.DEBUG
TRACE_DEFAULT_FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
TRACE_FILENAME = "ragcli.log"
TRACE_MAXBYTES = 10000
TRACE_LOGGER = "FULLRAG"
TRACE_MSG_LENGTH = 200
RAGCLI_LOGFILE_ENV = "RAGCLI_LOGFILE"
FAISS_DEFAULT_NAME = "faiss"
FAISS_DEFAULT_STORE = "./vstore"

# LLM stuff
SEMCHUNK_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_MODEL = "paraphrase-mpnet-base-v2"
OLLAMA_LOCAL_URL = "http://localhost:11434/api"
OLLAMA_DEFAULT_LLM = "tinydolphin"
LLM_DEFAULT_TEMPERATURE = 0.9
SM_DEFAULT_NEAREST = 3
CHKS_DEFAULT_SIZE = 500
CHKS_DEFAULT_OVERLAP = 50
CHKS_DEFAULT_SEP = "."

# Prompts
PROMPT_RAG_TEMPLATE = "Question: {prompt}\n Please answer the question based on the informations listed below: {context}"
ITEM_CONTEXT_TEMPLATE_LINE = "Context {i}: {contextItem}"

# Output status
OUT_ERROR = "ERROR"
OUT_SUCCESS = "SUCCESS"

# Output TAGs
TAG_O_RESPONSE = "<response>"
TAG_C_RESPONSE = "</response>"
TAG_O_LOG = "<log>"
TAG_C_LOG = "</log>"
TAG_O_ERROR = "<error>"
TAG_C_ERROR = "</error>"
TAG_O_STATUS = "<status>"
TAG_C_STATUS = "</status>"

# Command line arguments
ARG_READER = ["reader", "Document Reader type"]
ARG_READER_VALPYPDF = "pymupdf"
ARG_READER_VALLLAMAPARSE = "llamaparse"
ARG_KEY = ["key", "API's key"]
ARG_PROMPT = ["prompt", "Prompt to send to the LLM"]
ARG_PROMPT_TEMPLATE = ["template", "Prompt template to use when building the prompt (must contain {prompt} and {context}"]
ARG_TEMP = ["temperature", "LLM Temperature parameter, by defaul 0.9"]
ARG_PDFFILE = ["pdf", "PDF file path"]
ARG_TXTFILE = ["txt", "Text file path"]
ARG_CHUNKS = ["chunks", "JSON file path which contains the chunks"]
ARG_CHUNKTYPE = ["chunktype", "Type of chunking method"]
ARG_CHUNKTYPE_VALCHAR = "character"
ARG_CHUNKTYPE_VALSEM = "semantic"
ARG_FAISSNAME = ["faissname", "FAISS Index reference name"]
ARG_FAISSPATH = ["faisspath", "FAISS Index reference path (FAISS index and data storage)"]
ARG_CHUNKSIZE = ["chunk_size", "Chunk Size"]
ARG_CHUNKOVAP = ["chunk_overlap", "Chunk Overlap"]
ARG_SEP = ["sep", "Separator for chunking"]
ARG_NEAREST = ["nearest", "Faiss Number of nearest chunks to gather for prompting"]
ARG_MODEL = ["model", "Ollama Model installed"]
ARG_URL = ["urlbase", "URL for Ollama API (default localhost)"]
ARG_EMBEDDINGS = ["embeddings", "JSON file path which contains the data and embeddings"]
ARG_EMBEDDINGS_PT = ["embprompt", "JSON file path which contains the data and embeddings for the prompt"]
ARG_EMBEDDINGS_CK = ["embchunks", "JSON file path which contains the data and embeddings for the chunks"]
ARG_FAISSACTION = ["action", "Action to execute on the FAISS Engine (store/indexsearch/memsearch)"]
ARG_FAISSACTION_VALMSEARCH = "memsearch"
ARG_FAISSACTION_VALISEARCH = "indexsearch"
ARG_FAISSACTION_VALSTORE = "store"
ARG_NEARESTFILE = ["nfile", "JSON file path which contains the nearest chunks/texts"]

# Llamaparse
LLAMAPARSE_API_URL = "https://api.cloud.llamaindex.ai/api/parsing"
LLAMAPARSE_API_WAITSEC = 2
LLAMAINDEX_API_KEY = "LLAMAINDEX_API_KEY"