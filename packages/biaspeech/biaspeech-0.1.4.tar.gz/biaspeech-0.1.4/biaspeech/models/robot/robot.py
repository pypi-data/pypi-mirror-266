# --------------------------
# Models folder
# Class definition
#
# Bia : define the Bia model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config

""" objects:  """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks.block import Block
from biaspeech.models.blocks.arduino import Arduino
from biaspeech.models.blocks.alexa import Alexa
from biaspeech.models.blocks.camera import Camera
from biaspeech.models.blocks.display import Display
from biaspeech.models.blocks.web import Web
from biaspeech.models.blocks.radio import Radio
from biaspeech.models.blocks.tv import Tv
from biaspeech.models.blocks.youtube import Youtube
from biaspeech.models.blocks.netflix import Netflix
from biaspeech.models.blocks.python import Python
from biaspeech.models.blocks.macro import Macro
from biaspeech.models.blocks.default import Default
from biaspeech.utils.lang import Lang

""" objects creation logging and config """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

class Bia:
    
    """ constructor """
    def __init__(self, prompt, ai): 
        
        """ attributes """  
        self.conf = Config() # config
        self.logger = logging.getLogger(__name__) # logger        
        self.ai = ai # OpenAI object
        self.prompt = prompt # prompt object
        
        """ initialize """  
        self.lang_utils = Lang() # lang
        
        tp = self.prompt.mia.type # prompt type, like question, alexa etc
        if tp == "alexa": 
            self.block = Alexa(prompt, ai) # block for alexa
        elif tp == "arduino":
            self.block = Arduino(prompt, ai) # block for arduino
        elif tp == "camera":
            self.block = Camera(prompt, ai) # block for camera
        elif tp == "display":
            self.block = Display(prompt, ai) # block for display
        elif tp == "web":
            self.block = Web(prompt, ai) # block for web
        elif tp == "netflix":
            self.block = Netflix(prompt, ai) # block for netflix
        elif tp == "radio":
            self.block = Radio(prompt, ai) # block for radio
        elif tp == "tv":
            self.block = Tv(prompt, ai) # block for tv
        elif tp == "youtube":
            self.block = Youtube(prompt, ai) # block for youtube
        elif tp == "python":
            self.block = Python(prompt, ai) # block for python
        elif tp == "macro":
            self.block = Macro(prompt, ai) # block for macro
        else:
            self.block = Default(prompt, ai) # default block (for other types like question etc)
            
        self.set_file() # set the file

    """ set_file """        
    def set_file(self):
        file = self.prompt.mia.file
        if file == "": # no cache found 
            file = self.block.get_file() # for polymorph blocks like arduino, build the code and store it into the file 
        
        self.prompt.mia.file = file # update mia w the file
                    
    """ get_output """        
    def get_output(self):
        output = self.prompt.mia.output.lower()
        output_en = self.prompt.mia.output_en.lower()
        if output == "": # no cache found 
            self.logger.info("no cache found") # inform the user  
            
            output = self.block.get_output() # get output     
            self.prompt.mia.output = output.lower() # update mia 
            
            output_en = self.lang_utils.get_translate(output, self.prompt.mia.lang, conf.LANG_TO) # back tranlation                                               
            self.prompt.mia.output_en = output_en.lower() # update mia 

        else:
            self.logger.info("cache found") # inform the user  
            
        self.logger.info("output : " + output.lower()) # inform the user   
        self.logger.info("output_en : " + output_en.lower()) # inform the user   
                                      
        return output 

    """ run """        
    def run(self):   
        self.block.run(self.prompt.mia.file) # running 
    
    """ save """        
    def save(self):   
        if str(self.prompt.type) in conf.BACKPROPAGATE: # positive or negative feedback
            self.logger.info("backpropagation") # inform the user 
            self.prompt.mia.backpropagate() # back propagation 
        
        if str(self.prompt.type) == "macro": # macro
            self.logger.info("macro") # inform the user 
            self.prompt.mia.macro() # macro   
                  
        self.prompt.mia.save() # save
