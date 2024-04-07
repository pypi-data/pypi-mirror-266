# --------------------------
# Models folder
# Class definition
#
# Python : define the Python (Block) model
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


class Python(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)

    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_PYTHON)
 
    """ get_file """        
    def get_file(self):
        self.logger.info("get_file")  # inform the user     
        
        search = self.prompt.mia.input.replace("python", "")  # search
        input_en = conf.PYTHON_INPUT_B + search + conf.PYTHON_INPUT_C  # build the inout for OpenAI
        
        code_raw = self.ai.get_output_nolimit(input_en)  # ask OpenAI an arduino code
        
        code_raw = code_raw.replace("==", "in")  # replace
        code_raw = code_raw.replace("!=", "not in")  # replace
        
        code = conf.PYTHON_INPUT_A + code_raw
        
        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")  # put to string nice format
        fname = conf.PYTHON_FOLDER + date_time + ".py"  # build the folder / file name         
        
        file = open(fname, 'a')  # open up the file
        file.write(code)  # write
        file.close()  # close
        
        return(fname)
               
    """ run """        
    def run(self, file):
        try: 
            print(file)
            self.logger.info("python code generated")  # inform the user    
            os.popen("python3 " + file)
        
        except Exception as err:
            self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
            self.text2Speech.do_speech(conf.PROBLEM)  # inform the user
            self.logger.warning(f"conf.ERR_D {err=}, {type(err)=}")  # inform the user
      
