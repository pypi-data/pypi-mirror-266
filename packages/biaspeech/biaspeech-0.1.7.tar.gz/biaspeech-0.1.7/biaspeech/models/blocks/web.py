# --------------------------
# Models folder
# Class definition
#
# Web : define the Web (Block) model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config
import webbrowser

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks import block


class Web(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_WEB)
 
    """ get_file """        
    def get_file(self):
        pass
       
    """ run """        
    def run(self, file):
        self.logger.info("run w Web")  # inform the user     
        
        url = self.prompt.mia.input.replace("web ", "")
        url = url.replace("http://", "")
        url = "http://" + url
        
        webbrowser.open(url)
     
