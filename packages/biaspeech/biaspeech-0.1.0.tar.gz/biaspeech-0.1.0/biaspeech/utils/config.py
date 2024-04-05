# --------------------------
# Utils folder
# Class definition
#
# Config : constants
# --------------------------

""" imports: logging and config """
import os
import pathlib
from pathlib import Path
import configparser
        
""" config """
path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "config.cfg")
config = configparser.ConfigParser()
config.read(config_path)

class Config:

    """ constructor """
    def __init__(self): 
        parent = str(pathlib.Path(__file__).parent.parent.resolve()) # parent path 

        # read the arduino section of the config
        self.ARDUINO_INPUT_B = config.get("arduino", "input_b") # prompt text
        self.ARDUINO_FOLDER = parent + config.get("arduino", "folder") # folder to store ino file

        self.ARDUINO_PROGRAM = config.get("arduino", "program") # arduino program
        self.ARDUINO_BOARD = config.get("arduino", "board") # arduino board
        self.ARDUINO_PORT = config.get("arduino", "port") # arduino port
        self.ARDUINO_ACTIVE = config.get("arduino", "active") # arduino active

        # read the bia section of the config
        self.OUTPUT_ALEXA = config.get("bia", "output_alexa") # output by type
        self.OUTPUT_ARDUINO = config.get("bia", "output_arduino") # output by type
        self.OUTPUT_CAMERA = config.get("bia", "output_camera") # output by type
        self.OUTPUT_DISPLAY = config.get("bia", "output_display") # output by type
        self.OUTPUT_WEB = config.get("bia", "output_web") # output by type
        self.OUTPUT_RADIO = config.get("bia", "output_radio") # output by type
        self.OUTPUT_TV = config.get("bia", "output_tv") # output by type
        self.OUTPUT_YOUTUBE = config.get("bia", "output_youtube") # output by type
        self.OUTPUT_NETFLIX = config.get("bia", "output_netflix") # output by type
        self.OUTPUT_PYTHON = config.get("bia", "output_python") # output by type
        self.OUTPUT_MACRO = config.get("bia", "output_macro") # output by type
        
        # read the python section of the config
        self.CAMERA_FOLDER = parent + config.get("camera", "folder") # folder                  

        # read the error section of the config
        self.ERR_A = config.get("error", "err_a") # language
        self.ERR_B = config.get("error", "err_b") # language
        self.ERR_C = config.get("error", "err_c") # language
        self.ERR_D = config.get("error", "err_d") # language
                        
        # read the logging section of the config
        self.LOGLEVEL = config.get("logging", "level") # logging level 

        # read the main section of the config        
        self.OS = os.environ['OS'] # OS : macos or raspberry
        
        self.UI = config.get("main", "ui") # UI : keyboard or voice 
        self.MESSAGE = config.get("main", "message") # message 
        self.NOPROBLEM = config.get("main", "noproblem") # no problem 
        self.PROBLEM = config.get("main", "problem") # problem 
        self.VERSION = config.get("main", "version") # version 
        self.HELP = config.get("main", "help") # help 
        self.HELP_APP = config.get("main", "help_app") # help  app
        self.MAN = config.get("main", "man") # man
        self.WOMAN = config.get("main", "woman") # woman
        self.BACKGROUND = config.get("main", "background") # background
        self.WIDTH = int(config.get("main", "width")) # width
        self.HEIGHT = int(config.get("main", "height")) # height
                                                
        # read the openAI section of the config
        self.INPUT_MAX = config.get("openAI", "input_max") # input max
        
        # read the prompt section of the config
        self.LANG_TO = config.get("prompt", "lang_to") # pivot lang we convert to
        self.POSITIVE = config.get("prompt", "positive") # keyword for nltk
        self.NEGATIVE = config.get("prompt", "negative") # keyword for nltk
        self.NEUTRAL = config.get("prompt", "neutral") # keyword for nltk
        self.WEIGHT_AVG = config.getint("prompt", "weight_avg") # to trigger he type of prompt with the weight. Under this limit a weight will not trigger a type
        self.WEIGHT_MIN = config.getint("prompt", "weight_min") # to trigger a cache. Under this limit a mom or grandma with this weight will not be considered 
 
                
        # read the python section of the config
        self.PYTHON_INPUT_B = config.get("python", "input_b") # prompt text  
        self.PYTHON_INPUT_C = config.get("python", "input_c") # prompt text  
        self.PYTHON_FOLDER = parent + config.get("python", "folder") # folder to store the py file                 

        # read the speech2Text section of the config
        self.LANGUAGE = config.get("speech2Text", "language") # language
        self.RECORDING = parent + config.get("speech2Text", "recording") # recording
        self.RECORD = config.get("speech2Text", "record") + " " + self.RECORDING # recording
        self.ADJUST = config.getfloat("speech2Text", "adjust") # adjust
        self.TIMEOUT = config.getfloat("speech2Text", "timeout") # timeout
                                
        # read the sqlite section of the config
        self.DATABASE = parent + config.get("sqlite", "database") # database file 
                
        # read the text2Speech section of the config
        self.LANGUAGE = config.get("text2Speech", "language") # language 
        self.RATE = config.getint("text2Speech", "rate") # rate
        self.VOLUME = config.getfloat("text2Speech", "volume") # volume
        self.VOICE_MACOS = config.get("text2Speech", "voice_macos") # voice (3=Amelie, 38=Thomas)                                     
        self.VOICE_RASPBERRY = config.get("text2Speech", "voice_raspberry") # voice                               
        
        # read the web section of the config
        self.NETFLIX = config.get("web", "netflix") # netflix 
        self.RADIO = config.get("web", "radio") # radio       
        self.TV = config.get("web", "tv") # radio      
        self.YOUTUBE = config.get("web", "youtube") # youtube  
                        
        # other constants, not read in the config file
        self.WORDS = (["alexa"],
            ["bia", "robot"],
            ["camera"],
            ["display"],
            ["web", "internet"],
            ["radio"],
            ["tv"],
            ["youtube"],
            ["netflix"],
            ["python"],
            ["macro"],
            ["what", "why", "when", "where", "name", "is", "how", "do", "does", "which", "are", "could", "would", 
             "should", "has", "have", "whom", "whose", "don't"]) # key words to identify the prompt type

        self.TYPES = ("alexa", "arduino", "camera", "display", "web", "radio", "tv", "youtube", "netflix", "python", "macro", 
            "question","positive", "negative", "neutral") # prompt types
        
        self.CACHED = ("arduino", "python", "macro", "web", "radio", "tv", "youtube", "netflix", "question","positive", "negative", "neutral") # cached types, w WEIGHT_MIN
        
        self.FORCE_CACHED = ("positive", "negative", "neutral", "arduino") # cached types, whatever WEIGHT_MIN
        
        self.BACKPROPAGATE = ("positive", "negative", "neutral") # backpropagation types

        self.ARDUINO_INPUT_A = """ I have those examples :
  Otto.walk(2,1000,1); //2 steps, "TIME". IF HIGHER THE VALUE THEN SLOWER (from 600 to 1400), 1 FORWARD
  Otto.walk(2,1000,-1); //2 steps, T, -1 BACKWARD 
  Otto.turn(2,1000,1);//3 steps turning LEFT
  Otto._tone(10, 3, 1);
  Otto.bendTones (100, 200, 1.04, 10, 10);
    Otto.home();
    delay(100);  
  Otto.turn(2,1000,-1);//3 steps turning RIGHT 
  Otto.bend (1,500,1); //usually steps =1, T=2000
  Otto.bend (1,2000,-1);     
  Otto.shakeLeg (1,1500, 1);
    Otto.home();
    delay(100);
  Otto.shakeLeg (1,2000,-1);
  Otto.moonwalker(3, 1000, 25,1); //LEFT
  Otto.moonwalker(3, 1000, 25,-1); //RIGHT  
  Otto.crusaito(2, 1000, 20,1);
  Otto.crusaito(2, 1000, 20,-1);
    delay(100); 
  Otto.flapping(2, 1000, 20,1);
  Otto.flapping(2, 1000, 20,-1);
    delay(100);        
  Otto.swing(2, 1000, 20);
  Otto.tiptoeSwing(2, 1000, 20);
  Otto.jitter(2, 1000, 20); //(small T)
  Otto.updown(2, 1500, 20);  // 20 = H "HEIGHT of movement"T 
  Otto.ascendingTurn(2, 1000, 50);
  Otto.jump(1,500); // It doesn't really jumpl ;P
  Otto.home();
     delay(100); 
  Otto.sing(S_cuddly);
  Otto.sing(S_OhOoh);
  Otto.sing(S_OhOoh2);
  Otto.sing(S_surprise);
  Otto.sing(S_buttonPushed);       
  Otto.sing(S_mode1);        
  Otto.sing(S_mode2);         
  Otto.sing(S_mode3);  
  Otto.sing(S_sleeping);
  Otto.sing(S_fart1);
  Otto.sing(S_fart2);
  Otto.sing(S_fart3);
  Otto.sing(S_happy);
  Otto.sing(S_happy_short);                   
  Otto.sing(S_superHappy);   
  Otto.sing(S_sad);               
  Otto.sing(S_confused);
  Otto.sing(S_disconnection);
    delay(100);  
  Otto.playGesture(OttoHappy);
  Otto.playGesture(OttoSuperHappy);
  Otto.playGesture(OttoSad);
  Otto.playGesture(OttoVictory); 
  Otto.playGesture(OttoAngry); 
  Otto.playGesture(OttoSleeping);
  Otto.playGesture(OttoFretful);
  Otto.playGesture(OttoLove);
  Otto.playGesture(OttoConfused);        
  Otto.playGesture(OttoFart);
  Otto.playGesture(OttoWave);
  Otto.playGesture(OttoMagic);
  Otto.playGesture(OttoFail); 
  
  Start the code with :
  #include <Otto.h>
  Otto Otto;

  #define LeftLeg 2 // left leg pin, servo[0]
  #define RightLeg 3 // right leg pin, servo[1]
  #define LeftFoot 4 // left foot pin, servo[2]
  #define RightFoot 5 // right foot pin, servo[3]
  #define Buzzer 13 //buzzer pin

  void setup() {
    Otto.init(LeftLeg, RightLeg, LeftFoot, RightFoot, true, Buzzer);
    Otto.home();
  }
  
  please write a full code with the setup and loop methods to make the robot """

        self.PYTHON_INPUT_A = """# ** Polymorph code generated by openai :
# --------------------------
# Python folder
# Class definition
#
# Test : test the python polymorph code. In the program the 
#         code is generated by openai and stored in the python folder
# --------------------------

from controllers.base import Controller
import logging
import logging.config

from controllers.base import Controller

controller = Controller()

"""

    """ write """
    def write(self, section, option, value):
        config.set(section, option, value) # set the vqlue
        with open(config_path, 'w') as configfile: # write the file
            config.write(configfile)

             
        
