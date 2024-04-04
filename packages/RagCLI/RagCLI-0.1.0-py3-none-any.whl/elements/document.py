__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import fitz # pip install PyMuPDF
from langchain.text_splitter import CharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
import utils.CONST as C
import os
import mimetypes
import requests
import time

class document:
    def __init__(self, __filepath):
        self.__filepath = __filepath
        self.__content = ""
        
    @property
    def filepath(self) -> str: 
        return self.__filepath
    
    @property
    def content(self) -> str: 
        return self.__content
    
    def readTextFile(self) -> bool:
        try:
            with open(self.filepath, "r", encoding=C.ENCODING) as f:
                self.__content = f.read()
            return True
        except Exception as e:
            return False

    def pyMuPDFParseDocument(self, fromPage=0, toPage=0, heightToRemove=0) -> bool:
        """ Read a pdf file and add the content as text by using PyMuPDF

        Args:
            fromPage (int, optional): Starts from page Number. Defaults to 0.
            toPage (int, optional): Ends at page Number. Defaults to 0.
            heightToRemove (int, optional): Height in pixel to remove (header and footer). Defaults to 0.

        Returns:
            bool: True if no errors
        """
        try:
            reader = fitz.open(self.__filepath)
            for numPage, page in enumerate(reader): # iterate the document pages
                toPage = len(reader) if (toPage == 0) else toPage 
                if (numPage+1 >= fromPage and numPage+1 <= toPage):
                    pageBox = page.artbox
                    rect = fitz.Rect(pageBox[0], 
                                    pageBox[1] + heightToRemove, 
                                    pageBox[2], 
                                    pageBox[3] - heightToRemove)
                    self.__content = self.__content + page.get_textbox(rect) # get plain text encoded as UTF-8
            return True
        except Exception as e:
            return False
        
    def __wrapChunks(self, docs):
        nbChunks = len(docs)
        jsonInputs = {}
        jsonInputs["chunks"] = [ x.page_content for x in docs ] 
        return nbChunks, jsonInputs

    def characterChunking(self, separator, chunk_size, chunk_overlap):
        """ Chunks the document content into several pieces/chunks and returns a json text with the chunks
            format : {'chunks': ['Transcript of ...', ...] }
            Note: Leverage character langchain to manage the chunks

        Args:
            separator (str): Chunks separator
            chunk_size (str): chunk size
            chunk_overlap (str): chunk overlap

        Returns:
            str: A JSON text which looks like this: {'chunks': ['Transcript of ...', ...] }
        """
        try: 
            text_splitter = CharacterTextSplitter(separator = separator, 
                                                chunk_size = chunk_size, 
                                                chunk_overlap = chunk_overlap, 
                                                length_function = len, 
                                                is_separator_regex = False)
            docs = text_splitter.create_documents([self.__content])
            return self.__wrapChunks(docs) 
        except Exception as e:
            return -1, {}
    
    def semanticChunking(self):
        """Chunks the document content into several pieces/chunks and returns a json text with the chunks
            format : {'chunks': ['Transcript of ...', ...] }
            Note: Leverage semantic langchain to manage the chunks

        Returns:
            str: A JSON text which looks like this: {'chunks': ['Transcript of ...', ...] }
        """
        try: 
            hf_embeddings = HuggingFaceEmbeddings()
            model_name = C.SEMCHUNK_EMBEDDING_MODEL
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': False}
            hf_embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs=model_kwargs,
                    encode_kwargs=encode_kwargs,
                    )
            text_splitter = SemanticChunker(hf_embeddings)
            docs = text_splitter.create_documents([self.__content])
            return self.__wrapChunks(docs) 
        except Exception as e:
            return -1, {}
        
    def llamaParseDocument(self, extractType="markdown"):
        """ Read a pdf file and add the content as text by using llamaparse
            the LLAMAINDEX_API_KEY environment variable must be set to the API Key
            Cf.
                Login : https://cloud.llamaindex.ai/login
                Docs : https://docs.llamaindex.ai/
                Post : https://medium.com/llamaindex-blog/introducing-llamacloud-and-llamaparse-af8cedf9006b
                Example : https://github.com/allthingsllm/llama_parse/blob/main/examples/demo_api.ipynb
        Args:
            extractType (str): Extraction type text or markdown (default)
            
        Returns:
            bool: True if no errors
        """
        # Get the LLamaIndex Key from the LLAMAINDEX_API_KEY environment variable

        try:
            try:
                llamaIndexKey = os.environ[C.LLAMAINDEX_API_KEY]
            except:
                raise Exception ("The {} environment variable needs to be defined to use llamaparse.".format(C.LLAMAINDEX_API_KEY))
            # Upload the file
            headers = {"Authorization": f"Bearer {llamaIndexKey}"}
            
            with open(self.filepath, "rb") as f:
                mime_type = mimetypes.guess_type(self.filepath)[0]
                files = {"file": (f.name, f, mime_type)}
                # send the request, upload the file
                url_upload = f"{C.LLAMAPARSE_API_URL}/upload"
                response = requests.post(url_upload, headers=headers, files=files) 
                
            response.raise_for_status()
            # get the job id for the result_url
            job_id = response.json()["id"]
            url_result = f"{C.LLAMAPARSE_API_URL}/job/{job_id}/result/{extractType}"
            # check for the result until its ready
            while True:
                response = requests.get(url_result, headers=headers)
                if response.status_code == 200:
                    break
                time.sleep(C.LLAMAPARSE_API_WAITSEC)

            # download the result
            result = response.json()
            self.__content = result[extractType]
            
        except Exception as e:
            return -1, {}