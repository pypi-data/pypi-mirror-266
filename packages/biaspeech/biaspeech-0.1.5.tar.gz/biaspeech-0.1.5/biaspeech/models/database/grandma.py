# --------------------------
# Models folder
# Class definition
#
# Grandma : CRUD for grandma table
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

class Grandma:
    
    """ constructor """
    def __init__(self, id, input_en, paraphrase_en, w_distance, datetime): 
        
        self.id = id
        self.input_en = input_en 
        self.paraphrase_en = paraphrase_en 
        self.w_distance = w_distance
        self.datetime = datetime
    
    """ save """
    def save(self):
        sql = """
            insert into grandma ( input_en, paraphrase_en, w_distance, datetime)
            values (?, ?, ?, datetime())
            """
            
        CURSOR.execute(sql, ( self.input_en, self.paraphrase_en, self.w_distance))
        CONN.commit()
        
        self.id = CURSOR.lastrowid 

    """ get_orphan """
    def get_orphan(cls):
        sql = """    
        select distinct input_en as input_en
        from mia
        where input_en not in (select distinct input_en from grandma)
        group by input_en
        """        
        table_rows = CURSOR.execute(sql).fetchall()
          
        return (table_rows)
