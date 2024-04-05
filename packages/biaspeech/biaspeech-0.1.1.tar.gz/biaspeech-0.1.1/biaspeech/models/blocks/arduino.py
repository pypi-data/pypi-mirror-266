# --------------------------
# Models folder
# Class definition
#
# Arduino : define the Arduino (Block) model
# --------------------------

""" imports: logging, config, etc """
import logging
import logging.config
from biaspeech.utils.config import Config
from datetime import datetime
import pyduinocli
import os

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks import block
from biaspeech.utils.text2Speech import Text2Speech

class Arduino(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)

    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_ARDUINO)
 
    """ get_file """        
    def get_file(self):
        self.logger.info("get_file")  # inform the user     
        
        input_en = conf.ARDUINO_INPUT_A + self.prompt.mia.input_en + conf.ARDUINO_INPUT_B  # build the inout for OpenAI
        code_raw = self.ai.get_output_nolimit(input_en)  # ask OpenAI an arduino code
        
        code = code_raw
        
        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")  # put to string nice format
        folder = conf.ARDUINO_FOLDER + date_time
        fname = folder + "/" + date_time + ".ino"  # build the folder / file name        
        
        os.mkdir(folder)  # will save the file
        file = open(fname, 'a')  # open up the file
        file.write(code)  # write
        file.close()  # close
        
        return(folder)
               
    """ run """        
    def run(self, folder):
        try: 
            if conf.ARDUINO_ACTIVE == "1":  # arduino option on
                arduino = pyduinocli.Arduino(conf.ARDUINO_PROGRAM)  # program
                arduino.compile(fqbn=conf.ARDUINO_BOARD, sketch=folder)  # compile
                arduino.upload(fqbn=conf.ARDUINO_BOARD, sketch=folder, port=conf.ARDUINO_PORT)  # upload
                self.logger.info("arduino code uploaded")  # inform the user    
                            
            else:
                self.logger.info("arduino option is off")  # inform the user      
        
        except Exception as err:
            self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
            self.text2Speech.do_speech(conf.PROBLEM)  # inform the user
            self.logger.warning(f"conf.ERR_D {err=}, {type(err)=}")  # inform the user
