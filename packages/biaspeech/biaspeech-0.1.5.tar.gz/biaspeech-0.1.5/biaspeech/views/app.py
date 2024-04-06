# --------------------------
# Views folder
# Class definition
#
# App : define the base view, gui
# --------------------------

""" imports: logging, config, tkinter, threading, etc """
from biaspeech.utils.config import Config
from tkinter import ttk
from pathlib import Path
from tkinter import *
from pathlib import Path
import os
import logging
import logging.config
import tkinter as tk
import customtkinter
from PIL import Image, ImageTk

""" imports: MVC """
from biaspeech.utils.speech2Text import Speech2Text
from biaspeech.utils.text2Speech import Text2Speech
from biaspeech.controllers.asynch import Async
from biaspeech.controllers.action import Action

""" objects: logging and config """
path = Path(__file__)
ROOT_DIR = path.parent.absolute()
conf = Config() # config
        
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        """ util objects """
        self.logger = logging.getLogger(__name__) # logger
       
        """ init """
        self.title(conf.MESSAGE) # title
        self.action = Action() # action
  
        self.gui_canvas() # gui, canvas
        self.gui_images() # gui, images
        self.gui_buttons() # gui, buttons
        self.gui_texts() # gui, texts

    """ image_push """ 
    def image_push(self, event):  
        self.button_push()            
          
    """ button_push """ 
    def button_push(self):    
        old_text_in = "" # init
        self.speech2Text = Speech2Text(conf.LANGUAGE) # speech2Text  
        self.speech2Text.do_listen() # start listening
        self.text_in = self.speech2Text.get_input().lower() # STT input 
        
        if self.text_in != old_text_in and self.text_in != "": # something changed
            thread = Async(self.text_in) # asynch object
            thread.start() # start thread
            self.monitor(thread) # monitor
                    
            old_text_in = self.text_in # update
                
    """ monitor """ 
    def monitor(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.monitor(thread)) # check the thread every 100ms
            self.canvas.itemconfig(self.prompt, text='>> ' + self.text_in + '\n>> ...')
                    
        else:
            conf = Config() # config reload
            self.canvas.itemconfig(self.prompt, text='>> ' + self.text_in + '\n>> ' + thread.output)
            self.text2Speech = Text2Speech(conf.LANGUAGE, conf.RATE, conf.VOLUME, conf.VOICE_MACOS, conf.VOICE_RASPBERRY) # object for text2speech            
            self.text2Speech.do_speech(thread.output) # inform the user
        
    """ gui_canvas """
    def gui_canvas(self): # gui, canvas. Thanks to https://github.com/ParthJadhav/Tkinter-Designer
        geometry = str(conf.WIDTH) + 'x' + str(conf.HEIGHT)
        self.geometry(geometry)
        self.configure(bg = conf.BACKGROUND) # background
        
        self.canvas = Canvas( # canvas
            self,
            bg = conf.BACKGROUND,
            height = 519 * conf.HEIGHT / 519,
            width = 862 * conf.WIDTH / 862,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        
        self.canvas.place(x = 0, y = 0)

    def gui_images(self): # gui, images
        file_path = os.path.join(ROOT_DIR, r'frame0/robot.png') # robot image
        image_robot = PhotoImage(file = file_path) 

        one = PhotoImage(file=file_path)
        self.one = one  # to prevent the image garbage collected.
        id_image_robot = self.canvas.create_image((490 * conf.HEIGHT / 519, 0), image=one, anchor='nw')
        self.canvas.tag_bind(id_image_robot, '<Button-1>', self.image_push)

    def gui_buttons(self): # gui, buttons
        custom_font = ("Roboto Bold", 25 * -1)
        button_push = customtkinter.CTkButton(master=self, text="PUSH TO TALK", font=custom_font, width=400 * conf.WIDTH / 862, height=150 * conf.HEIGHT / 519, compound="top", command=self.button_push) # button
        button_push.pack(padx=20 * conf.WIDTH / 862, pady=20 * conf.HEIGHT / 519) # push
        button_push.configure(hover_color="orange")        

        self.canvas_widget = self.canvas.create_window(680 * conf.WIDTH / 862, 50 * conf.HEIGHT / 519, window=button_push) # button

        file_path = os.path.join(ROOT_DIR, r'frame0/man.jpeg') # robot image
        image = customtkinter.CTkImage(Image.open(file_path), size=(50 * conf.WIDTH / 862, 50 * conf.HEIGHT / 519))
        button_man = customtkinter.CTkButton(master=self, text="", width=50 * conf.WIDTH / 862, height=50 * conf.HEIGHT / 519, compound="top", image=image, command=self.action.button_man) # button
        button_man.pack(pady=50 * conf.HEIGHT / 519, padx=50 * conf.WIDTH / 862) # man 
        self.canvas_widget = self.canvas.create_window(150 * conf.WIDTH / 862, 485 * conf.HEIGHT / 519, window=button_man) # button

        file_path = os.path.join(ROOT_DIR, r'frame0/woman.jpg') # robot image
        image = customtkinter.CTkImage(Image.open(file_path), size=(50 * conf.WIDTH / 862, 50 * conf.HEIGHT / 519))
        button_woman = customtkinter.CTkButton(master=self, text="", width=50 * conf.WIDTH / 862, height=50 * conf.HEIGHT / 519, compound="top", image=image, command=self.action.button_woman) # button
        button_woman.pack(pady=50 * conf.HEIGHT / 519, padx=50 * conf.WIDTH / 862) # man 
        self.canvas_widget = self.canvas.create_window(235 * conf.WIDTH / 862, 485 * conf.HEIGHT / 519, window=button_woman) # button
        
        button_speed_m = customtkinter.CTkButton(master=self, text="--", width=50 * conf.WIDTH / 862, height=50 * conf.HEIGHT / 519, compound="top", command=self.action.button_speed_m) # button
        button_speed_m.pack(pady=50 * conf.HEIGHT / 519, padx=50 * conf.WIDTH / 862) # rate   
        self.canvas_widget = self.canvas.create_window(320 * conf.WIDTH / 862, 485 * conf.HEIGHT / 519, window=button_speed_m) # button
                    
        button_speed_p = customtkinter.CTkButton(master=self, text="++", width=50 * conf.WIDTH / 862, height=50 * conf.HEIGHT / 519, compound="top", command=self.action.button_speed_p) # button
        button_speed_p.pack(pady=50 * conf.HEIGHT / 519, padx=50 * conf.WIDTH / 862) # rate   
        self.canvas_widget = self.canvas.create_window(380 * conf.WIDTH / 862, 485 * conf.HEIGHT / 519, window=button_speed_p) # button
                                    
        button_help = customtkinter.CTkButton(master=self, text="?", width=50 * conf.WIDTH / 862, height=50 * conf.HEIGHT / 519, compound="top", command=self.action.button_help) # button
        button_help.pack(pady=50 * conf.HEIGHT / 519, padx=50 * conf.WIDTH / 862) # help
        self.canvas_widget = self.canvas.create_window(440 * conf.WIDTH / 862, 485 * conf.HEIGHT / 519, window=button_help) # button

    def gui_texts(self): # gui, texts
        self.canvas.create_text( # text main
            16.0 * conf.WIDTH / 862,
            15.0 * conf.HEIGHT / 519,
            anchor="nw",
            text="Hey I am BIA :-)",
            fill="#FCFCFC",
            font=("Roboto Bold", 28 * -1)
        )
        
        self.canvas.create_rectangle(
            24.0 * conf.WIDTH / 862,
            78.0 * conf.HEIGHT / 519,
            84.0 * conf.WIDTH / 862,
            83.0 * conf.HEIGHT / 519,
            fill="#FCFCFC",
            outline="")
        
        self.canvas.create_text( # text second
            22.0 * conf.WIDTH / 862,
            85.0 * conf.HEIGHT / 519,
            anchor="nw",
            text=" your AI robot",
            fill="#FFFFFF",
            font=("Roboto Bold", 20 * -1)
        )
        
        self.canvas.create_text( # text prompt
            24.0 * conf.WIDTH / 862,
            145.0 * conf.HEIGHT / 519,
            width=690 * conf.WIDTH / 862,
            anchor="nw",
            text=">> yes? oui? wie kann ich dir helfen? como puedo ayudarte? 我怎么帮你 ",
            fill="#FFFFFF",
            font=("Roboto Bold", 18 * -1)
        )
        
        self.prompt = self.canvas.create_text( # text prompt second
                        24.0 * conf.WIDTH / 862,
                        220.0 * conf.HEIGHT / 519,
                        width=690 * conf.HEIGHT / 519,
                        anchor="nw",
                        text=">> ...",
                        fill="#FFFFFF",
                        font=("Roboto Bold", 18 * -1))    
                 
        self.canvas.create_text( # text prompt third
            20.0 * conf.WIDTH / 862,
            490.0 * conf.HEIGHT / 519,
            anchor="nw",
            text=conf.VERSION,
            fill="#FFFFFF",
            font=("Roboto Bold", 6 * -1)
        )  
        
        self.canvas.pack()
        #window.resizable(False, False)

