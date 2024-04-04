__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from elements.embeddingsFactory import embeddingsFactory
from rag import rag
from elements.FAISSWrapper import FAISSWrapper
import utils.CONST as C

"""
    usage: RagQueryFaiss [-h] 
                         -prompt PROMPT 
                         [-temperature TEMPERATURE] 
                         [-nearest NEAREST] 
                         [-model MODEL]
                         [-urlbase URLBASE] 
                         -faissname FAISSNAME 
                         -faisspath FAISSPATH
"""

def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_PROMPT[0], help=C.ARG_PROMPT[1], required=True)
        parser.add_argument("-" + C.ARG_TEMP[0], help=C.ARG_TEMP[1], required=False, type=float, default=0.9)
        parser.add_argument("-" + C.ARG_NEAREST[0], help=C.ARG_NEAREST[1], required=False, type=int, default=3)
        parser.add_argument("-" + C.ARG_MODEL[0], help=C.ARG_MODEL[1], required=False, default="tinydolphin")
        parser.add_argument("-" + C.ARG_URL[0], help=C.ARG_URL[1], required=False, default="http://localhost:11434/api")
        parser.add_argument("-" + C.ARG_FAISSNAME[0], help=C.ARG_FAISSNAME[1], required=True)
        parser.add_argument("-" + C.ARG_FAISSPATH[0], help=C.ARG_FAISSPATH[1], required=True)
        args = vars(parser.parse_args())
        myRag.init(args)

        # 1 - Text embeddings
        embFactory = embeddingsFactory()
        vPrompt = myRag.textEmbeddings(embFactory, args[C.ARG_PROMPT[0]])
        # 2 - Load the existing index
        myfaiss = FAISSWrapper()
        myRag.FAISSLoad(myfaiss, args[C.ARG_FAISSPATH[0]], args[C.ARG_FAISSNAME[0]])
        # 3 - Similarity Search
        similars = myRag.FAISSSearch(myfaiss, args[C.ARG_NEAREST[0]], vPrompt)
        # 4 - Build prompt
        customPrompt = myRag.buildPrompt(args[C.ARG_PROMPT[0]], similars["text"])
        # 5 - Ask to the LLM ...
        resp = myRag.promptLLM(customPrompt, args[C.ARG_URL[0]], args[C.ARG_MODEL[0]], args[C.ARG_TEMP[0]])

        myRag.output(resp)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()