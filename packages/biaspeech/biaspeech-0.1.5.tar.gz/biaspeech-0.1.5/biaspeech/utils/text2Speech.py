# --------------------------
# Models folder
# Class definition
#
# Text2Speech : define the text to speech model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config

""" imports: pyttsx3 """
import pyttsx3 
        
""" objects:  """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

class Text2Speech:    

    """ constructor """
    def __init__(self, language, rate, volume, voice_macos, voice_raspberry): 

        """ util objects """
        self.logger = logging.getLogger(__name__) # logger

        """ attributes """
        self.language = language # language
        self.rate = rate # rate
        self.volume = volume # volume
        self.voice_macos = voice_macos # voice
        self.voice_raspberry = voice_raspberry # voice
        
    """ do_speech """        
    def do_speech(self, text):
        try:          
            engine = pyttsx3.init()
                 
            engine.setProperty('language', self.language) # language
            engine.setProperty('rate', self.rate) # speech rate (words per minute), default is 200
            engine.setProperty('volume', self.volume) # volume (0.0 to 1.0), default is 1.0 
            
            if conf.OS == "macos":
                engine.setProperty('voice', self.voice_macos)  # voice          
            else:
                engine.setProperty('voice', self.voice_raspberry)  # voice      
              
            
            engine.say(text) # say some
            engine.runAndWait() # go
            
        except Exception as err:
            self.logger.warning(f"conf.ERR_D {err=}, {type(err)=}") # inform the user
            raise
