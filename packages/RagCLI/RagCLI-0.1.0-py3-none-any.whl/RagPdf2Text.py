__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from rag import rag
import utils.CONST as C

"""
    Read a PDF file and converts it into text.
    2 readers available:
        1) Using pymupdf
        2) using llamaparse
           Note: the env. variable LLAMAINDEX_API_KEY must be set with the llamaindex key
    usage: RagPdf2Text [-h] 
                       -pdf {PDF file and path} 
                       -txt {Text file and path}  
                       [-reader {pymupdf,llamaparse}]
"""

def main():
    parser = argparse.ArgumentParser()
    myRag = rag()
    try:
        parser.add_argument("-" + C.ARG_PDFFILE[0], help=C.ARG_PDFFILE[1], required=True)
        parser.add_argument("-" + C.ARG_TXTFILE[0], help=C.ARG_TXTFILE[1], required=True)
        parser.add_argument("-" + C.ARG_READER[0], help=C.ARG_TXTFILE[1], required=False, 
                            choices=[C.ARG_READER_VALPYPDF, C.ARG_READER_VALLLAMAPARSE],
                            default=C.ARG_READER_VALPYPDF)
        args = vars(parser.parse_args())
        myRag.init(args)

        # 1 - Read the pdf content
        pdf = myRag.readPDF(args[C.ARG_PDFFILE[0]], args[C.ARG_READER[0]])
        if not myRag.writeToFile(args[C.ARG_TXTFILE[0]], pdf.content):
            raise Exception("Impossible to write the content into the file")
        myRag.output(C.OUT_SUCCESS)

    except Exception as e:
        parser.print_help()
        myRag.output(C.OUT_ERROR, True, str(e))
        
if __name__ == "__main__":
    main()