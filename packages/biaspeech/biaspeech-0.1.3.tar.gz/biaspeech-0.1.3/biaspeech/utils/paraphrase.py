# --------------------------
# Utils folder
# Class definition
#
# Paraphrase : paraphrase
# --------------------------

""" imports: logging, parrot """
import logging
import logging.config
from biaspeech.utils.config import Config
#from parrot import Parrot
import parrot

""" objects:  """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.database.grandma import Grandma

class Paraphrase:

    """ constructor """
    def __init__(self): 
        
        """ util objects """
        self.conf = Config() # config
        self.logger = logging.getLogger(__name__) # logger

        """ attributes """        
        self.parrot = Parrot()
        self.grandma = Grandma(0, "", "", "", "")  
        
    """ set_paraphrase """
    def set_paraphrase(self):
        phrases = self.grandma.get_orphan()
                
        for phrase in phrases:
           paraphrases = self.parrot.augment(input_phrase=phrase[0])
           self.logger.info("searching paraphrase for : " + phrase[0]) # inform the user   

           if paraphrases:
               for paraphrase in paraphrases:
                   self.logger.info(paraphrase) # inform the user   
                   
                   self.grandma = Grandma(0, phrase[0], paraphrase[0], paraphrase[1], "") # new line in grandma
                   self.grandma.save()  
