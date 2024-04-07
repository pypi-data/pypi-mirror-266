# ---------
# BIA program
# - --
# IA personal assistant. BIA is OpenAI based vocal assistant. 
# Extra cool functionality, BIA also provides IA to the educational Otto robot.
#
# Nicolas Christophe (nicolas.christophe@gmail.com)
#
# Versions
#  - v1.0 15.04.2023 Creation
# ---------

""" imports: logging, config and language libs """
import logging
import logging.config
from biaspeech.utils import config
import sys

""" imports: MVC """
from biaspeech.controllers.base import Controller
from biaspeech.utils.config import Config

""" main """
def biaspeech():       
    """ controller:  """
    logger = logging.getLogger(__name__) # logger
            
    controller = Controller() # object for controller    
    if len(sys.argv) == 1: # no argument given
        controller.start_server() # starts the server, interactive mode
        
    else:
        if sys.argv[1] == "-help":
            controller.help()
        elif sys.argv[1] == "-update":
            controller.update()
        elif sys.argv[1] == "-version":
            controller.version()
        else:
            controller.process(sys.argv[1]) # unit mode, process only one input
    
 
if __name__ == "__main__":
    biaspeech() # let's go 
    
