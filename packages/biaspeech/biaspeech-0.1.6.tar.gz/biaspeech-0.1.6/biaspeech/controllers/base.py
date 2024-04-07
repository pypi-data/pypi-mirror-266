# --------------------------
# Controller folder
# Class definition
#
# Controller : define the base controller
# --------------------------

""" imports: logging and config """
from biaspeech.utils.config import Config
import logging
import logging.config

""" imports: MVC """
from biaspeech.utils.paraphrase import Paraphrase
from biaspeech.utils.config import Config
from biaspeech.utils.speech2Text import Speech2Text
from biaspeech.utils.text2Speech import Text2Speech
from biaspeech.models.openAI.ai import AI
from biaspeech.models.robot.robot import Bia
from biaspeech.models.speech.prompt import Prompt
from biaspeech.views.ui import UI
from biaspeech.views.app import App

""" objects: logging and config """
conf = Config()  # config


class Controller:
    
    """ constructor """
    def __init__(self):

        """ util objects """
        self.logger = logging.getLogger(__name__)  # logger
        
        """ attributes """   
        self.ai = AI()  # object for openAI
        
    """ start_server """      
    def start_server(self): 
        old_text_in = ""
        if conf.UI == "keyboard":  # keyboard
            self.ui_view = UI()  # view object, ui
            while True:
                text_in = self.ui_view.get_prompt("? ")  # text prompt
                if text_in != old_text_in and text_in != "":  # something changed
                    self.process(text_in)  # process                     
                    old_text_in = text_in  # update

        elif conf.UI == "voice": # voice
            self.speech2Text = Speech2Text(conf.LANGUAGE) # speech2Text  
            while True:
                self.speech2Text.do_listen() # start listening
                text_in = self.speech2Text.get_input().lower() # STT input 
                if text_in != '' and text_in != old_text_in:
                    self.process(text_in)  # process                     
                    old_text_in = text_in  # update

        else:  # gui
            self.app_view = App()  # view object, app
            self.app_view.mainloop()  # open the app            
    
    """ process """   
    def process(self, text_in):
        prompt = Prompt(text_in)  # prompt object  
        bia = Bia(prompt, self.ai)  # bia object
                
        bia.run()  # run the action if any    
        output = bia.get_output()  # get the output
        
        self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY)  # object for text2speech            
        self.text2Speech.do_speech(output)  # inform the user
            
        bia.save()  # save to sqlite

        return output
    
    """ help """   
    def help(self): 
        print(conf.HELP)  # help
        
    """ update """   
    def update(self): 
        self.paraphrase = Paraphrase()  # paraphrase              
        self.paraphrase.set_paraphrase()  # update the paraphrase table
        
    """ version """   
    def version(self): 
        print(conf.VERSION)  # version

