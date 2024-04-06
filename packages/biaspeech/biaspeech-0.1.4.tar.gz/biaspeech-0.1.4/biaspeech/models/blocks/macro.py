# --------------------------
# Models folder
# Class definition
#
# Macro : define the Macro (Block) model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config
from datetime import datetime
import os

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks import block
from biaspeech.utils.text2Speech import Text2Speech


class Macro(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)

    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_MACRO)
 
    """ get_file """        
    def get_file(self):
        pass
    
    """ run """        
    def run(self, file):
        pass
      
