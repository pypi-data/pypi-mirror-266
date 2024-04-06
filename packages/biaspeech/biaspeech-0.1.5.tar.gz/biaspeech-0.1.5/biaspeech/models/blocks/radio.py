# --------------------------
# Models folder
# Class definition
#
# Radio : define the Radio (Block) model
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


class Radio(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_RADIO)
 
    """ get_file """        
    def get_file(self):
        pass
       
    """ run """        
    def run(self, file):
        self.logger.info("run w Radio")  # inform the user     
        
        search = self.prompt.mia.input.replace("radio ", "")  # build the url
        url = conf.RADIO  # build the url
        
        if search != "":  # build the url
            url = url + "search?q=" + search
        
        webbrowser.open(url)  # open-up the url
     
