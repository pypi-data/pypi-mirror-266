# --------------------------
# Models folder
# Class definition
#
# Mia_utils : utils for mia table
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

class Mia_utils:
    
    """ constructor """
    def __init__(self): 
        pass
    
    """ get_input_en """
    def get_input_en(cls, input, lang):
        sql = """    
        select input_en 
        from mia
        where input = ? and lang = ?
        order by w_neutral desc, w_positive desc, datetime desc
        limit 1
        """        
        table_rows = CURSOR.execute(sql, (input, lang)).fetchall()

        return (table_rows)  
    
