__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from rag import rag
import utils.CONST as C
from elements.embeddingsFactory import embeddingsFactory

"""
    Create embeddings:
        1) from a single string (prompt)
        2) from a list of chunks (JSON)
            Format -> {'chunks': ['Transcript of ...', ...] }
    usage: RagEmbeddings [-h] 
                         -embeddings {File and path for the embeddings / JSON}
                         [-chunks {List of chunks in a JSON format}] 
                         [-prompt {prompt}] 
"""

def getArg(arg, name):
    try:
        return arg[name]
    except:
        return C.NULLSTRING

def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_CHUNKS[0], help=C.ARG_CHUNKS[1], required=False, default=C.NULLSTRING)
        parser.add_argument("-" + C.ARG_PROMPT[0], help=C.ARG_PROMPT[1], required=False, default=C.NULLSTRING)
        parser.add_argument("-" + C.ARG_EMBEDDINGS[0], help=C.ARG_EMBEDDINGS[1], required=True)
        args = vars(parser.parse_args())
        myRag.init(args)

        # We must have a lit of chunks or a prompt, otherwise -> Exception
        chunks = getArg(args, C.ARG_CHUNKS[0])
        prompt = getArg(args, C.ARG_PROMPT[0])
        if (chunks == C.NULLSTRING and prompt == C.NULLSTRING or 
            chunks != C.NULLSTRING and prompt != C.NULLSTRING):
            raise Exception("A prompt or a list of chunks must be provided, but not both!")

        embFactory = embeddingsFactory()
        if (prompt != C.NULLSTRING):
            embeddings = myRag.textEmbeddings(embFactory, args[C.ARG_PROMPT[0]])
        else:
            # Get the chunks first as list
            chunks = myRag.readJsonFromFile(args[C.ARG_CHUNKS[0]])
            embeddings = myRag.chunkEmbeddings(embFactory, chunks)

        # Write the json in a file 
        if (not myRag.writeJsonToFile(args[C.ARG_EMBEDDINGS[0]],  embeddings)):
            raise Exception("Impossible to write the embeddings in a file")
        
        myRag.output(C.OUT_SUCCESS)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()