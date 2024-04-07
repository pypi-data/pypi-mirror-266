# --------------------------
# Models folder
# Class definition
#
# Prompt : define the prompt model
# --------------------------

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config
        
""" objects:  """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
import nltk
from nltk import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from biaspeech.models.database.mia import Mia
from biaspeech.models.database.mia_utils import Mia_utils
from biaspeech.utils.lang import Lang

class Prompt:
    
    """ constructor """
    def __init__(self, input):     
            
        """ util objects """
        self.conf = Config() # config
        self.logger = logging.getLogger(__name__) # logger
        self.lang_utils = Lang() # lang

        """ attributes """                
        self.input = input.lower() # input
        self.lang = self.lang_utils.get_lang(self.input) # detect the lang
        self.input_en = "" # input_en
        self.set_lang(); # set the input_en
        self.weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
        
        self.has_mom = False # mom found in the cache
        self.has_grandma = False # grandma found in the cache
        
        """ initialize """
        self.set_weight_words() # set the weight for each type, example question=100, etc
        self.set_weight_sentiment() # set the 3 weights positive, negative, neutral   
        self.set_type() # set the type, like question, etc
        self.set_mia() # create the ia object (= database table entry line object)
        self.set_cache() # cache management, do we have a mom or grandma relevant answer?
        
        """ inform the user """
        self.logger.info("input : " + self.input) # inform the user  
        self.logger.info("input_en : " + self.input_en) # inform the user  
        self.logger.info("weights : " + str(self.weights)) # inform the user
        self.logger.info("type : " + str(self.type)) # inform the user

    """ set_lang """         
    def set_lang(self):
        self.mia_utils = Mia_utils()
        res = self.mia_utils.get_input_en(self.input, self.lang)

        if len(res) > 0: # search a translation in mia if any
            self.input_en = ''.join(res[0])

        if self.input_en == "":  
            self.input_en = self.lang_utils.get_translate(self.input, self.lang, self.conf.LANG_TO) # translate to EN, pivot language
        

    """ set_weight words """         
    def set_weight_words(self):        
        from nltk.tokenize import word_tokenize
        question = self.input_en
        question = question.lower()
        question = word_tokenize(question)
        
        i = 0
        while i < len(self.weights):   
            if any(x in question[0] for x in self.conf.WORDS[i]):
                self.weights[i] = 100       
            i = i + 1 
                            
    """ set_weight sentiment """        
    def set_weight_sentiment(self):
        sia = SentimentIntensityAnalyzer()
        vs = sia.polarity_scores(self.input_en)

        self.weights.append(vs[self.conf.POSITIVE] * 100)
        self.weights.append(vs[self.conf.NEGATIVE] * 100)
        self.weights.append(vs[self.conf.NEUTRAL] * 100)

    """ set_type """        
    def set_type(self):
        self.type = "question"
        i = 0
        while i < len(self.weights):               
            if self.weights[i] > self.conf.WEIGHT_AVG:
                self.type = self.conf.TYPES[i]
                return
            i = i + 1 
         
    """ set_mia """
    def set_mia(self):
        self.mia = Mia.create(0, self.type, self.lang, self.input, self.input_en, "", "", "",
            self.weights[0], self.weights[1], self.weights[2], self.weights[3], self.weights[4], self.weights[5], 
            self.weights[6], self.weights[7], self.weights[8], self.weights[9], self.weights[10], self.weights[11], 
            self.weights[12], self.weights[13], self.weights[14], 0, "")  

    """ set_cache """
    def set_cache(self): 
        if self.type in self.conf.CACHED: # if the type is cache relevant
            self.set_mom() # mom object
            self.set_grandma() # grandma object
            self.set_update_mia() # if cache relevant copy cache to mia
                       
    """ set_mom """
    def set_mom(self):          
        if len(self.mia.get_mom(self.input_en)) > 0:
            self.mom = self.mia.get_mom(self.input_en)[0] # search for a parent in the mia table
            self.has_mom = True # set the attribute          
            
    """ set_grandma """
    def set_grandma(self):
        if len(self.mia.get_grandma(self.input_en)) > 0:
            self.grandma = self.mia.get_grandma(self.input_en)[0] # search for parent in the grandma table
            self.has_grandma = True # set the attribute
                            
    """ set_update_mia """
    def set_update_mia(self):
        if self.has_mom: # mom found
            w_positive_mom = self.mom.w_positive # get the weight of the mom
            w_neutral_mom = self.mom.w_neutral # get the weight of the mom
           
            if w_positive_mom >= self.conf.WEIGHT_MIN or self.type in conf.FORCE_CACHED or w_neutral_mom == 100: # if valid cache        
                self.mia = self.mom 
                return
               
        if self.has_grandma: # grandma found
            w_positive_grandma = self.grandma.w_positive # get the weight of the grandma
            w_neutral_grandma = self.grandma.w_neutral # get the weight of the grandma
                    
            if w_positive_grandma >= self.conf.WEIGHT_MIN or self.type in conf.FORCE_CACHED or w_neutral_grandma == 100: # if trigger reached
                self.mia = self.grandma # grandma cache found is valid, set it
