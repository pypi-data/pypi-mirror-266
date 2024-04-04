__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from rag import rag
import utils.CONST as C

"""
    Build a prompt based on a template. The template must contain the {context} and {prompt} tags inside.
    By default: "Question: {prompt}\n Please answer the question based on the informations listed below: {context}"

    usage: RagPrompt [-h] 
                     -prompt {question to ask to the LLM} 
                     -nfile {list of the nearest chunks / json}
                     [-template {template string}] 
"""
def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_PROMPT[0], help=C.ARG_PROMPT[1], required=True)
        parser.add_argument("-" + C.ARG_PROMPT_TEMPLATE[0], help=C.ARG_PROMPT_TEMPLATE[1], required=False, 
                            default = C.PROMPT_RAG_TEMPLATE)
        parser.add_argument("-" + C.ARG_NEARESTFILE[0], help=C.ARG_NEARESTFILE[1], required=True)
        args = vars(parser.parse_args())
        
        myRag.init(args)
        nearest = myRag.readJsonFromFile(args[C.ARG_NEARESTFILE[0]])
        resp = myRag.buildPrompt(args[C.ARG_PROMPT[0]], nearest)
        myRag.output(resp)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()