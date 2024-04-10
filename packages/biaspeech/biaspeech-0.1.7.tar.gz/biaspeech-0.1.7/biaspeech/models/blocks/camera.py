# --------------------------
# Models folder
# Class definition
#
# Camera : define the Camera (Block) model
# --------------------------

""" imports: logging and config, datetime, time, opencv """
import logging
import logging.config
from biaspeech.utils.config import Config
import time
from datetime import datetime
import cv2

""" objects:  """
conf = Config()  # config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=conf.LOGLEVEL)

""" MVC """
from biaspeech.models.blocks import block


class Camera(block.Block):
    
    """ constructor """
    def __init__(self, prompt, ai): 
        block.Block.__init__(self, prompt, ai)
        
    """ get_output """        
    def get_output(self): 
        return(conf.OUTPUT_CAMERA)

    """ get_file """        
    def get_file(self):
        pass
        
    """ run """        
    def run(self, file):
        self.logger.info("run w Camera")  # inform the user

        now = datetime.now()  # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")  # put to string nice format
        fname = conf.CAMERA_FOLDER + date_time + ".jpg"  # build the folder / file name
        
        cam = cv2.VideoCapture(0)  # capture
        s, img = cam.read()  # read
        if s:  # all good
            # WINDOW_NAME = 'Pic pic'
            # cv2.startWindowThread()
            # cv2.imshow(WINDOW_NAME,img)
            # cv2.waitKey(0) 
            # cv2.destroyAllWindows()
            # cv2.waitKey(1) 
            cv2.imwrite(fname, img)  # write

        else: 
            self.logger.info("no image detected")  # inform the user
        
