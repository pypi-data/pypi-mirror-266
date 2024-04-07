# --------------------------
# Models folder
# Class definition
#
# Display : define the Display (Block) model
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


class Display(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_DISPLAY)

    """ get_file """        
    def get_file(self):
        pass
        
    """ run """        
    def run(self, file):
        self.logger.info("run w Display")  # inform the user          
