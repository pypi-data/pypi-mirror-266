# --------------------------
# Models folder
# Class definition
#
# Default : define the Default (Block) model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks import block


class Default(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self): 
        self.logger.info("asking OpenAI")  # inform the user
          
        return(self.ai.get_output(self.prompt.input))  # ask OpenAI
    
    """ get_file """        
    def get_file(self):
        pass
              
    """ run """        
    def run(self, file):
        pass
