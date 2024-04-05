# --------------------------
# Deploy folder
#
# setup definition
# --------------------------

from setuptools import setup

__project__ = "biaspeech"
__version__ = "0.1.0"
__description__ = "BIA (AI), your AI powered vocal assistant"
__long_description__ = "The module is documented on instructables : https://www.instructables.com/BIA-AI-Your-IA-Powered-Vocal-Assistant-instructabl/ <br>BIA(AI) © 2024 by Nicolas CHRISTOPHE is licensed under CC BY-NC-ND 4.0. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/"
__packages__ = ["biaspeech", "biaspeech.utils", "biaspeech.controllers", "biaspeech.models.blocks", "biaspeech.models.database", "biaspeech.models.openAI", "biaspeech.models.robot", "biaspeech.models.speech", "biaspeech.data", "biaspeech.views", "biaspeech.bin"]
__author__ = "TylerDDDD"
__author_email__ = "makertylerdddd@gmail.com"
__classifiers__ = [
	"Development Status :: 3 - Alpha", 
	"Intended Audience :: Education", 
	"Programming Language :: Python :: 3",
]
__readme__ = "README.md"
__keywords__ = ["robot", "otto", "ai", "vocal", "assistant",]
__requires__ = ["nltk", "openai", "websockets", "argostranslate", "py3langid", "pyautogui", "pyaudio", "speechrecognition", "pyttsx3", "parrot", "opencv-python", "customtkinter", "pyduinocli"]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    long_description = __long_description__,
    packages = __packages__,
    author = __author__,
    author_email = __author_email__,
    classifiers = __classifiers__,
    readme = __readme__,
    keywords = __keywords__,
    install_requires = __requires__,
    package_data={'': ['bin/*', 'views/frame0/*', 'utils/*cfg', 'data/*', 'data/arduino/*', 'data/camera/*', 'data/logs/*', 'data/python/*', 'README.md', 'LICENSE']},
    include_package_data=True,
)

