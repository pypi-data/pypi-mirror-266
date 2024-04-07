# --------------------------
# Models folder
# Class definition
#
# Block : define the Block model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.speech import prompt
from biaspeech.models.openAI import ai


class Block:
    
    """ constructor """
    def __init__(self, prompt, ai): 
        
        self.logger = logging.getLogger(__name__)  # logger
        self.prompt = prompt  # prompt
        self.ai = ai  # ai

    """ get_output """        
    def get_output(self):
        pass

    """ get_file """        
    def get_file(self):
        pass
                    
    """ run """        
    def run(self, file):
        pass
