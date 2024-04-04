__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.CONST as C

class prompt:
    def __init__(self, myquestion, mycontext):
        self.__question = myquestion
        self.__context = mycontext  # Pandas Serie
        self.__template = C.PROMPT_RAG_TEMPLATE

    @property
    def template(self):
        return self.__template
    @template.setter
    def template(self, t):
        self.__template = t
        
    @property
    def question(self):
        return self.__question
    @question.setter
    def question(self, q):
        self.__question = q
    
    @property
    def context(self):
        return self.__context
    @context.setter
    def context(self, q):
        self.__context = q
    
    def build(self):
        try: 
            itemContext = ""
            for i, item in self.context.items():
                itemContext = itemContext + C.ITEM_CONTEXT_TEMPLATE_LINE.format(i=i, contextItem=item) + "\n"
            return self.template.format(prompt=self.question, context=itemContext)
        except:
            return ""