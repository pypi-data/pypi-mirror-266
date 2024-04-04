__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from rag import rag
import utils.CONST as C

""" 
    Prompt a LLM managed by Ollama and returns the response.
    usage: RagLLM [-h] 
                  -prompt {question to the LLM} 
                  [-model {Ollama Model installed}] 
                  [-urlbase {Ollama URL base, def http://localhost:11434/api}] 
                  [-temperature {Model temperature, def 0.9}]
"""

def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_PROMPT[0], help=C.ARG_PROMPT[1], required=True)
        parser.add_argument("-" + C.ARG_MODEL[0], help=C.ARG_MODEL[1], required=False, default=C.OLLAMA_DEFAULT_LLM)
        parser.add_argument("-" + C.ARG_URL[0], help=C.ARG_URL[1], required=False, default=C.OLLAMA_LOCAL_URL)
        parser.add_argument("-" + C.ARG_TEMP[0], help=C.ARG_TEMP[1], required=False, type=float, default=C.LLM_DEFAULT_TEMPERATURE)
        args = vars(parser.parse_args())
        
        myRag.init(args)
        resp = myRag.promptLLM(args[C.ARG_PROMPT[0]], args[C.ARG_URL[0]], args[C.ARG_MODEL[0]], args[C.ARG_TEMP[0]])
        myRag.output(resp)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()