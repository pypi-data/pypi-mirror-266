__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from elements.embeddingsFactory import embeddingsFactory
from rag import rag
import utils.CONST as C

"""
    usage: 
"""

def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_PDFFILE[0], help=C.ARG_PDFFILE[1], required=True)
        parser.add_argument("-" + C.ARG_FAISSNAME[0], help=C.ARG_FAISSNAME[1], required=True)
        parser.add_argument("-" + C.ARG_FAISSPATH[0], help=C.ARG_FAISSPATH[1], required=True)
        parser.add_argument("-" + C.ARG_CHUNKSIZE[0], help=C.ARG_CHUNKSIZE[1], required=False, type=int, default=500)
        parser.add_argument("-" + C.ARG_CHUNKOVAP[0], help=C.ARG_CHUNKOVAP[1], required=False, type=int, default=50)
        parser.add_argument("-" + C.ARG_SEP[0], help=C.ARG_SEP[1], required=False, default=".")
        args = vars(parser.parse_args())
        myRag.init(args)

        # 1 - Read the pdf content
        pdf = myRag.readPDF(args[C.ARG_PDFFILE[0]])
        # 2 - Chunk document
        nb, chunks = myRag.characterchunking(pdf, args[C.ARG_SEP[0]], args[C.ARG_CHUNKSIZE[0]], args[C.ARG_CHUNKOVAP[0]])
        embFactory = embeddingsFactory()
        # 3 - Chunks embeddings
        vChunks = myRag.chunkEmbeddings(embFactory, chunks)
        # 4 - Store embeddings in the index
        myRag.FAISSStore(vChunks,  C.ARG_FAISSPATH[0],  args[C.ARG_FAISSNAME[0]])

        myRag.output(C.OUT_SUCCESS)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()