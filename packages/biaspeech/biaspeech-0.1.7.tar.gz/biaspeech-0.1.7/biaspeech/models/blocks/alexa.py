# --------------------------
# Models folder
# Class definition
#
# Alexa : define the Alexa (Block) model
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


class Alexa(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self):
        return(self.conf.OUTPUT_ALEXA)

    """ get_file """        
    def get_file(self):
        pass
        
    """ run """        
    def run(self, file):
        self.logger.info("run w Alexa")  # inform the user 
        
