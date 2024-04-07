## **BIA (IA)**, your **IA powered vocal assistant**. 

## Pitch:
-  **BIA** is an **IA powered vocal assistant**. BIA brings all in one ChatGPT, 
voice command, YouTube, Netflix, TV, Radio and web navigation. 
- **BIA** is multi language and can interact via the voice or command line. Can run 
on any laptop, and even on a Raspberry.
- Extra cool functionality, **BIA** also provides IA to the educational **Otto robot**. Historically, 
**Otto** is a world-wide known open source robot used for educational and fun purpose. **BIA** 
brings **Otto** to the next level. Yes, you can now have a conversation with the robot, 
ie asking him to execute dynamic actions (danse, walk, make sounds, and so on). 
- A **double layer IA mechanism** provide fast and accurate answers : one layer powered 
by OpenAI, and a second layer processed by a native AI manages the cache and the 
smart actions (complex requests), ensuring better and faster answers.

## Basic usage of BIA, **app mode** :
- First, install the prerequesite, as per described in the installation section below
- Open a terminal, then type : 

	python3 run.py

- The Bia app will open, just push the button and ask a question. Bia will answer ... Enjoy :)

## Lazy usage of BIA, **voice mode** :
- Open a terminal, then type : 

	python3 run.py

- The app will not open but the service is listening.. Ask a question. Bia will answer ... Enjoy :)

Note : the **UI** parameter under the **[main]** section must be set to "voice". 
The config file can be found under <<python package>>/utils/config.cfg

## Advanced usage of BIA, **command line mode** :
- Open a terminal, then type : 

	python3 run.py "what can I do a friday afternoon in Paris?"
	python3 run.py -help
	python3 run.py -version

- Bia will answer ... Enjoy :)

## Developer usage of BIA, **keyboard mode** :
- Open a terminal, then type : 
	
	python3 run.py

- Write a question. Bia will answer ... Enjoy :)

Note : the **UI** parameter under the **[main]** section must be set to "keyboard". 
The config file can be found under <<python package>>/utils/config.cfg

## Example of some prompt :
- Quelle est la capitale de la France?
- How are you today?

## Advanced prompts :
- I do not like this answer => a negative prompt will decrease the scoring of the latest answer, it will go down in the cache
- I like this answer very much => a positive prompt will increase the scoring of the latest answer, it will stays up in the cache

## Skills. The special prompts are the following :
- **arduino** : ask the otto robot to do something => Example : Arduino dance the salsa
- **camera** : take a picture => Example : Camera now
- **macro** : save the last command as a keyword => Example : Macro salsa
- **netflix** : run netflix and search for a movie => Example : Netflix breaking bad
- **python** : run a combination of prompts => Example : Python if the capital of France is Paris then Arduino walk one meter
- **radio** : open the web radio site and search for a station => Example : Radio deutschlandfunk
- **tv** : open molotov tv => Example : TV m6
- **web** : open a website => Example : Web google.com
- **youtube** : open youtube and search for some => Example : Youtube dire straits

## Required hardware:
- Developed under MacOS Catalina version 10.15.7 and Python version 3.8
- Tested under Raspberry OS and Python version 3.9
- Headphone and microphone
- (optional) Arduino
- (optional) Raspberry PI
- (optional) Otto robot

## How to install on MacOS : 

 **A. Prerequesites :**
 
Download and install homebrew-4.2.4.pkg
Install one by one the libraries : 
	
	pip install openai
	pip install websockets
	pip install argostranslate
	pip install py3langid
	pip install pyautogui 
	pip install pyaudio
	pip install speechrecognition
	pip install pyttsx3
	pip install parrot
	pip install opencv-python --verbose
	pip install customtkinter
	pip install pyduinocli      
	
Install arduino-cli
	
	curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

Install the languages :
	
	argospm install translate-de_en
	argospm install translate-en_de
	etc with all the languages needed

Download the nltk ressources :
	pip install nltk
	python3
 	>>import nltk
 	>>nltk.download('punkt')
 	>>nltk.download('vader_lexicon')
 
 **B. Install the python package biaspeech :**
 
	pip install biaspeech

 **C. Create a file run.py :**
 
      import os
      os.environ['OPENAI_API_KEY'] = "xxxx" # openAI API key
      os.environ['OS'] = "macos"
      from biaspeech import biaspeech

## How to install on Raspberry OS : 

 **A. Prerequesites :**
 
Download the nltk ressources :
    
	pip install nltk 
	python3
	>>import nltk
	>>nltk.download('punkt')
	>>nltk.download('vader_lexicon')
	 
Install one by one the libraries : 
    
	sudo apt-get install libjpeg8-dev
 	sudo apt install espeak
	sudo apt install python3-opencv
	sudo apt-get install flac 
	pip install openai
	pip install websockets
 	pip install argostranslate
 	pip install py3langid
 	pip install pyautogui 
 	pip install pyaudio
 	pip install speechrecognition
 	pip install pyttsx3
 	pip install parrot
	pip install customtkinter
	pip install pyduinocli      
	
Install arduino-cli
	
	curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
	
Install the languages :
	
	argospm install translate-de_en
	argospm install translate-en_de
	etc with all the languages needed
	
Check the microphone configuration : https://www.pofilo.fr/post/2018/12/16-mic-raspberry-pi/

 **B. Install the python package biaspeech :**
 
	pip install biaspeech

 **C. Create a file run.py :**
 
	import os
    os.environ['OPENAI_API_KEY'] = "xxxx" # openAI API key
    os.environ['OS'] = "raspberry"
    from biaspeech import biaspeech
 
## Parameters to be checked and changed in the file config.cfg : 
- **UI** parameter under the **[main]** section, the possible values are :	
	"keyboard" (keyboard/command line mode) 
	"voice" (voice mode) 
	"app" for (app/gui mode)  

- Optional, parameters under the **[arduino]** section
- Others parameters are self explanatory

## Advanced tips : 
- Bia will **log into a file** when run with this command :

	python3 -u run.py > <<python package>>/data/logs/bia_"$(date +"%Y_%m_%d_%I_%M_%p").log" 2>&1

- The log files are stored under the folder <<python package>>/data/logs
- The log level can be changed with the **level** parameter under the **[logging]** section. The values can be INFO, ERROR, DEBUG
- Run from time to time the command below. This option will update the grandma table with the paraphrase of the prompts, this will improve the cache functionality

	python3 run.py -update


## Tyler Maker (makertylerdddd@gmail.com)

## Versions:
- v1.0 02.04.2024 Creation

