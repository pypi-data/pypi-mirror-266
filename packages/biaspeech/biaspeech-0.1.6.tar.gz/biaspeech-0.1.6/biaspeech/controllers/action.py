# --------------------------
# Controllers folder
# Class definition
#
# Action : action management
# --------------------------

""" imports: logging, etc """
from biaspeech.utils.config import Config
import logging
import logging.config

""" imports: MVC """
from biaspeech.utils.text2Speech import Text2Speech

conf = Config()  # config


class Action():
    
    def __init__(self):

       """ util objects """
       self.logger = logging.getLogger(__name__)  # logger
       logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)
       
    """ button_man """ 
    def button_man(self): 
        conf.VOICE_MACOS = "com.apple.speech.synthesis.voice.thomas"  # man voice
        conf.VOICE_RASPBERRY = "french"  # man voice

        conf.write("text2Speech", "voice_macos", "com.apple.speech.synthesis.voice.thomas")
        conf.write("text2Speech", "voice_raspberry", "french")  

        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
        self.text2Speech.do_speech(conf.MAN)  # inform the user
        
    """ button_woman """ 
    def button_woman(self): 
        conf.VOICE_MACOS = "com.apple.speech.synthesis.voice.amelie"  # woman voice
        conf.VOICE_RASPBERRY = "french+f3"  # mwoan voice

        conf.write("text2Speech", "voice_macos", "com.apple.speech.synthesis.voice.amelie")
        conf.write("text2Speech", "voice_raspberry", "french+f3")
    
        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
        self.text2Speech.do_speech(conf.WOMAN)  # inform the user

    """ button_speed_m """ 
    def button_speed_m(self): 
        conf.RATE = conf.RATE - 10  # rate
        conf.write("text2Speech", "rate", str(conf.RATE))

        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
        self.text2Speech.do_speech(str(conf.RATE))  # inform the user
        
    """ button_speed_p """ 
    def button_speed_p(self): 
        conf.RATE = conf.RATE + 10  # rate
        conf.write("text2Speech", "rate", str(conf.RATE))

        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
        self.text2Speech.do_speech(str(conf.RATE))  # inform the user
                                
    """ button_help """ 
    def button_help(self): 
        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech    
        self.text2Speech.do_speech(conf.HELP_APP)  # inform the user
        
