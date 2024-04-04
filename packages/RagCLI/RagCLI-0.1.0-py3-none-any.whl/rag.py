__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from elements.document import document
from elements.FAISSWrapper import FAISSWrapper
from elements.ollamaWrapper import ollamaWrapper
from elements.prompt import prompt
import json
from utils.traceOut import traceOut
import utils.CONST as C
from numpyencoder import NumpyEncoder
from utils.log import log
import os

class rag():
    def __init__(self):
        self.myTrace = traceOut()
        try:
            ragLogFileName = os.environ[C.RAGCLI_LOGFILE_ENV]
        except:
            ragLogFileName = C.TRACE_FILENAME
        self.__myLog = log(C.TRACE_LOGGER, ragLogFileName)

    def init(self, args):
        self.myTrace.initialize(args)
        self.myTrace.start()
        self.log.info("** START **")

    @property
    def trace(self):
        return self.myTrace
    @property
    def log(self):
        return self.__myLog
    
    def addTrace(self, name, description, *others):
        self.trace.add(name, description, others)
        self.log.info("Step {} -> {}".format(name, self.__fmtMsgForLog(description)))
    
    def __fmtMsgForLog(self, message, limit = C.TRACE_MSG_LENGTH):
        logMsg = message.replace("\n", " ")
        dots = ""
        if (len(message) > limit):
            dots = " ..."
        logMsg = logMsg[:limit] + dots
        return logMsg
    
    # Standard Output printing via XML tags
    def output(self, response, error = False, errorMsg = C.NULLSTRING):
        self.myTrace.stop()
        print(C.TAG_O_LOG + self.trace.getFullJSON() + C.TAG_C_LOG)
        if (error):
            self.log.error("Output: Response> {} | Error> {}".format(self.__fmtMsgForLog(response), errorMsg))
            print(C.TAG_O_STATUS + C.OUT_ERROR + C.TAG_C_STATUS)
            print(C.TAG_O_RESPONSE + errorMsg + C.TAG_C_RESPONSE)
        else:
            self.log.info("Output: Response> {}".format(self.__fmtMsgForLog(response)))
            print(C.TAG_O_RESPONSE + response + C.TAG_C_RESPONSE)
            print(C.TAG_O_STATUS + C.OUT_SUCCESS + C.TAG_C_STATUS)
        self.log.info("** STOP **")
        
    def readPDF(self, pdffile, method = C.ARG_READER_VALPYPDF):
        # Read the pdf content
        self.log.info("Read PDF file {}".format(pdffile))
        pdf = document(pdffile)
        if (method == C.ARG_READER_VALPYPDF):
            pdf.pyMuPDFParseDocument()
        else:
            pdf.llamaParseDocument()
        if (len(pdf.content) <= 0):
            raise Exception("Error while converting the PDF document to text")
        self.addTrace("PDF2TXT", "PDF converted to TEXT successfully. Text length : {}".format(len(pdf.content)))
        return pdf

    def characterchunking(self, doc, separator, size, overlap):
        # Chunk document
        nb, chunks = doc.characterChunking(separator, size, overlap)
        if (nb<=0):
            raise Exception("Error while chunking the document")
        self.addTrace("CHUNKING","Document (character) chunked successfully, Number of chunks : {}".format(nb), nb)
        return nb, chunks
    
    def semanticChunking(self, doc):
        # Chunk document
        nb, chunks = doc.semanticChunking()
        if (nb<=0):
            raise Exception("Error while chunking the document")
        self.addTrace("CHUNKING","Document (semantic) chunked successfully, Number of chunks : {}".format(nb), nb)
        return nb, chunks
    
    def textEmbeddings(self, embFactory, prompt):
        vPrompt = embFactory.createEmbeddingsFromTXT(prompt)
        if (vPrompt == {}):
            raise Exception("Error while creating the prompt embeddings")
        self.addTrace("PTEMBEDDGS", "Embeddings created from prompt successfully")
        return vPrompt

    def chunkEmbeddings(self, embFactory, chunks):
        vChunks = embFactory.createEmbeddingsFromList(chunks)
        if (vChunks == {}):
            raise Exception("Error while creating the chunks embeddings")
        self.addTrace("DOCEMBEDDGS", "Embeddings created from chunks successfully")
        return vChunks

    def FAISSaddToIndex(self, myfaiss, vChunks):
        myfaiss.addToIndex(vChunks)
        self.addTrace("ADDTOINDEX", "Add chunks to the FAISS Index")

    def FAISSSearch(self, myfaiss, k, vPrompt):
        similars = myfaiss.getNearest(vPrompt, k)
        self.addTrace("SIMILARSEARCH", "Similarity Search executed successfully")
        return similars

    def FAISSStore(self, vChunks, path, name):
        myfaiss = FAISSWrapper()
        myfaiss.addToIndex(vChunks)
        self.addTrace("FAISSSTORE", "Chunks embeddings indexed and stored successfully")
        myfaiss.save(path, name)
        return myfaiss

    def FAISSLoad(self, myfaiss, path, name):
        self.addTrace("FAISSSTORE", "Chunks embeddings indexed and stored successfully")
        myfaiss.load(path, name)

    def buildPrompt(self, question, similarText):
        myPrompt = prompt(question, similarText)
        customPrompt = myPrompt.build()
        if (len(customPrompt) == 0):
            raise Exception("Error while creating the prompt")
        self.addTrace("PROMPT", "Prompt built successfully", customPrompt)
        return customPrompt

    def promptLLM(self, question, urlOllama, model, temperature):
        myllm = ollamaWrapper(urlOllama, model, temperature)
        resp = myllm.prompt(question)
        self.addTrace("LLMPT", "LLM Reponse\n {}\n".format(resp))
        return resp

    def writeToFile(self, filename, content):
        try:
            self.log.info("Write to file {}".format(filename))
            with open(filename, "w", encoding=C.ENCODING) as f:
                f.write(content)
            return True
        except Exception as e:
            return False

    def writeJsonToFile(self, filename, jsonContent):
        try:
            self.log.info("Write to JSON file {}".format(filename))
            with open(filename, "w", encoding=C.ENCODING) as f:
                f.write(json.dumps(jsonContent, cls=NumpyEncoder))
            return True
        except Exception as e:
            return False
        
    def readJsonFromFile(self, filename):
        try:
            self.log.info("Read from JSON file {}".format(filename))
            with open(filename, "r", encoding=C.ENCODING) as f:
                data = json.load(f)
                return data
        except Exception as e:
            return {}