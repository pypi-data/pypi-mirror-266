# --------------------------
# Controllers folder
# Class definition
#
# Async : thread management w the app
# --------------------------

""" imports: logging, config, tkinter, threading, etc """
from biaspeech.utils.config import Config
import logging
import logging.config
from threading import Thread

""" imports: MVC """
from biaspeech.models.openAI.ai import AI
from biaspeech.models.robot.robot import Bia
from biaspeech.models.speech.prompt import Prompt

""" objects: logging and config """
conf = Config()  # config


class Async(Thread):
    
    def __init__(self, text_in):
       super().__init__()
       
       """ util objects """
       self.conf = Config()  # config
       self.logger = logging.getLogger(__name__)  # logger
               
       """ attributes """  
       self.text_in = text_in 
       self.ai = AI()  # object for openAI
       self.output = ""
        
    """ run """
    def run(self): 
       self.output = ""
       self.output = self.process(self.text_in)  # process 
 
    """ process """   
    def process(self, text_in):
        prompt = Prompt(text_in)  # prompt object  
        bia = Bia(prompt, self.ai)  # bia object
        output = bia.get_output().lower()  # get the output 
       
        bia.run()  # run the action if any    
        bia.save()  # save to sqlite    
                
        return output
