# --------------------------
# Utils folder
#
# Debug, lines to paste in the interpreter
# --------------------------

""" text to speech """
import pyttsx3
engine = pyttsx3.init()
#engine.setProperty('voice', 'french+f3') #my preference
engine.setProperty('voice', 'french')
engine.say("salut beau gosse") # say some
engine.runAndWait() # go
engine.stop() # stop
            
""" speech to text """
import speech_recognition as sr                                       
r = sr.Recognizer()                                                   
audio = sr.AudioFile("recording.wav")
with audio as source:
    audio = r.record(source)                  
    text = r.recognize_google(audio, language = 'fr_FR')
    
    print(format(text)) # format

import speech_recognition as sr 
recognizer = sr.Recognizer() # initialize the recognizer    
r = sr.Recognizer()                                                                                   
#with sr.Microphone(device_index = 3) as source: # set the deviceIndex         
with sr.Microphone(3) as source: # set the deviceIndex                                                              
    #recognizer.adjust_for_ambient_noise(source, duration=1) # w adjust duration
    recorded_audio = recognizer.listen(source) # listen
    text = recognizer.recognize_google(recorded_audio, language="fr_FR") # w language
    print(format(text)) # format

""" translate """
from translate import Translator
from langdetect import detect
from langdetect import DetectorFactory

text="quelle est la capitale de la france"
translator= Translator(from_lang="fr", to_lang="en")
result = translator.translate(text)
print(result)

result = detect(text)
print(result)

""" shell """
import os
stream = os.popen("arecord --format=S16_LE --duration=5 --rate=48000 ./data/recording.wav")
