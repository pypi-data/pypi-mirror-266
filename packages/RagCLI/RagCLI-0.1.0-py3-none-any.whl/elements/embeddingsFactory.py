__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from sentence_transformers import SentenceTransformer
import pandas as pd
import utils.CONST as C

"""
        Embeddings and data are stored and used here with the format :
        {0: {'text': 'How many jobs Joe Biden wants to create ?', 
             'embedding': array([-6.65125623e-02,  4.26685601e-01, -1.22626998e-01, -1.14275487e-02,
                                -1.76032424e-01, -2.55425069e-02,  3.19633447e-02,  1.10126780e-02,
                                -1.75059751e-01,  2.00320985e-02,  3.28031659e-01,  1.18581623e-01,
                                -9.89666581e-02,  1.68430805e-01,  1.19766712e-01, -7.14423656e-02, ...] 
            },
        1: {'text': '...', 
            'embedding': array([...]
            },
        ...
        }
"""

class embeddingsFactory:
    def __init__(self):
        try:
            self.__encoder = SentenceTransformer(C.EMBEDDING_MODEL)
        except:
            self.__encoder = None

    @property
    def encoder(self):
        return self.__encoder

    def __wrapEmbeddings(self, vectAndData):
        """ Wrap the Dataframe into a list (to have a json later)
        The Dataframe contains 2 columns: 
            1) text : with the data
            2) embedding: with the vector/embeddings calculated (as a nparray)
        Args:
            vectAndData (Dataframe): Data and embeddings
        Returns:
            {}: list for a later JSON conversion
        """
        textAndEmbeddings = {}
        for i, (chunk, vector) in enumerate(vectAndData):
            line = {}
            line["text"] = chunk
            line["embedding"] = vector
            textAndEmbeddings[i] = line
        return textAndEmbeddings

    def createEmbeddingsFromTXT(self, text):
        """ Calculate the embeddings for a single string
        Args:
            text (str): string or ine chunk
        Returns:
            str: json with data and embeddings
        """
        try: 
            jsonInputs = {}
            jsonInputs["chunks"] = [text]
            textAndEmbeddings = self.createEmbeddingsFromList(jsonInputs)
            return textAndEmbeddings
        except Exception as e:
            return {}

    def createEmbeddingsFromList(self, jsonChunks):
        """ Calculate the embeddings for list of chunks
        Args:
            jsonChunks ({}): List of chunks
        Returns:
            str: json with data and embeddings for all chunks
        """
        try: 
            if (self.encoder == None):
                raise Exception ("Encoder not initialized")
            dfInput = pd.DataFrame(jsonChunks["chunks"], columns=["chunks"])
            vect = self.encoder.encode(dfInput["chunks"])
            vectAndData = zip(dfInput["chunks"], vect)
            return self.__wrapEmbeddings(vectAndData)
        except Exception as e:
            return {}