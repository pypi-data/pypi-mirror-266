# --------------------------
# Models folder
# Class definition
#
# AI : define the artificial intelligence model
# --------------------------

""" imports: logging, config, etc """
import openai
#import os
from biaspeech.utils.config import Config
import logging
import logging.config

""" objects: logging, config, etc """
MODEL = "gpt-3.5-turbo"
conf = Config() # config
     
class AI:    
    
    """ constructor """
    def __init__(self): 
        """ util objects """
        self.logger = logging.getLogger(__name__) # logger
        
    """ ask something with a limit """        
    def get_output(self, input):
        input = input + ' ' + conf.INPUT_MAX
        try:          
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": input}]
            )
            output = response.choices[0].message.content.strip() # format the output
            return output

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    """ ask something without a limit """        
    def get_output_nolimit(self, input):
        try:          
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": input}]
            )
            output = response.choices[0].message.content.strip() # format the output
            return output

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

