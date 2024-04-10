# --------------------------
# Models folder
# Class definition
#
# Mia : CRUD for mia table
# --------------------------
from websockets.version import commit

""" imports: logging and config """
import logging
import logging.config
from biaspeech.utils.config import Config

""" imports: sqlite """
import sqlite3

""" objects: logging and config """
conf = Config() # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

CONN = sqlite3.connect(conf.DATABASE, check_same_thread=False) # connection to sqlite
CURSOR = CONN.cursor() # cursor

class Mia:
    
    """ constructor """
    def __init__(self, id_cache, type, lang, input, input_en, output, output_en, file,
                 w_alexa, w_arduino, w_camera, w_display, w_web, w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro,
                 w_question, w_positive, w_negative, w_neutral, backpropagation, datetime): 
        
        self.id_cache = id_cache
        self.type = type
        self.lang =lang
        self.input = input
        self.input_en = input_en 
        self.output = output
        self.output_en = output_en
        self.file = file
        self.w_alexa = w_alexa
        self.w_arduino = w_arduino
        self.w_camera = w_camera
        self.w_display = w_display
        self.w_web = w_web
        self.w_radio = w_radio  
        self.w_tv = w_tv
        self.w_youtube = w_youtube
        self.w_netflix = w_netflix
        self.w_python = w_python
        self.w_macro = w_macro
        self.w_question =  w_question
        self.w_positive = w_positive
        self.w_negative = w_negative
        self.w_neutral = w_neutral
        self.backpropagation = backpropagation
        self.datetime = datetime
    
    """ save """
    def save(self):
        sql = """
            insert into mia ( id_cache, type, lang, input, input_en, output, output_en, file,
                 w_alexa, w_arduino, w_camera, w_display, 
                 w_web, w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro,
                 w_question, w_positive, w_negative, w_neutral, backpropagation, datetime)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime())
            """
            
        CURSOR.execute(sql, ( self.id_cache, self.type, self.lang, self.input, self.input_en, 
            self.output, self.output_en, self.file, self.w_alexa, self.w_arduino, self.w_camera, 
            self.w_display, self.w_web, self.w_radio, self.w_tv, self.w_youtube, self.w_netflix, 
            self.w_python, self.w_macro, self.w_question, self.w_positive, self.w_negative, self.w_neutral, self.backpropagation))
            
        CONN.commit()
        self.id = CURSOR.lastrowid 

    """ back_propagate """
    def backpropagate(self):
        sql = """    
        update mia
            set w_positive = ?, w_negative = ?, w_neutral = ?, backpropagation = backpropagation + 1
            where type in ("arduino", "display", "python", "macro", "question")
            and input_en = (
                select input_en from mia
                where type in ("arduino", "display", "python", "macro", "question")
                order by datetime desc
                limit 1 
                )
        """    
            
        CURSOR.execute(sql, ( self.w_positive, self.w_negative, self.w_neutral ))
        CONN.commit
        
    """ macro """
    def macro(self):
        sql = """    
        update mia
            set input = ?, input_en = ?
            where input_en = (
                select input_en from mia
                where type <> 'macro'
                order by datetime desc
                limit 1 
                )
        """    
            
        input = self.input.replace("macro ", "") # cleanup
        input_en = self.input_en.replace("macro ", "") # cleanup
        
        CURSOR.execute(sql, ( input, input_en ))
        CONN.commit
        
    """ create """
    @classmethod 
    def create(cls, id_cache, type, lang, input, input_en, output, output_en, 
        file, w_alexa, w_arduino, w_camera, w_display, w_web, 
        w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro, 
        w_question, w_positive, w_negative, w_neutral, backpropagation, datetime):
        
        new_instance = cls(id_cache, type, lang, input, input_en, output, output_en,
            file, w_alexa, w_arduino, w_camera, w_display, w_web, 
            w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro, 
            w_question, w_positive, w_negative, w_neutral, backpropagation, datetime)
    
        return new_instance
    
    """ create_from_db """
    @classmethod
    def create_from_db(cls, table_row):
        new_instance = cls(table_row[1], table_row[2], table_row[3], table_row[4], table_row[5], table_row[6], table_row[7], 
            table_row[8], table_row[9], table_row[10], table_row[11], table_row[12], table_row[13], 
            table_row[14], table_row[15], table_row[16], table_row[17], table_row[18], table_row[19], table_row[20],
            table_row[21], table_row[22], table_row[23], table_row[24], table_row[25])
        
        new_instance.id = table_row[0]

        return new_instance 

    """ get_table_rows """
    @classmethod
    def get_table_rows(cls):
        sql = """    
            select * from mia
        """
        table_rows = CURSOR.execute(sql).fetchall()

        return [cls.create_from_db(row) for row in table_rows]
    
    """ get_mom """
    @classmethod
    def get_mom(cls, input_en):
        sql = """    
        select id, id, type, lang, 
            input, input_en, output, output_en,
            file, 
            w_alexa, w_arduino, w_camera, w_display, w_web, 
            w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro, 
            w_question, w_positive, w_negative, w_neutral, backpropagation, datetime()
        from mia
        where input_en = ?
        order by w_neutral desc, w_positive desc, datetime desc
        limit 1
        """        
        table_rows = CURSOR.execute(sql, (input_en,)).fetchall()

        return ([cls.create_from_db(row) for row in table_rows])   
    
    """ get_grandma """
    @classmethod
    def get_grandma(cls, input_en):
        sql = """    
        select mia.id, mia.id, type, lang, 
            grandma.input_en, grandma.input_en, output, output_en, 
            file,
            w_alexa, w_arduino, w_camera, w_display, w_web, 
            w_radio, w_tv, w_youtube, w_netflix, w_python, w_macro,
            w_question, w_positive, w_negative, w_neutral, backpropagation, datetime() 
        from mia
        join grandma on mia.input_en = grandma.input_en
        where grandma.paraphrase_en = ?
        order by w_neutral desc, w_positive desc, mia.datetime desc, grandma.w_distance desc
        limit 1
        """        
        table_rows = CURSOR.execute(sql, (input_en,)).fetchall()
          
        return ([cls.create_from_db(row) for row in table_rows])
