# --------------------------
# Views folder
# Class definition
#
# Ui : define the base UI view (keyboard and voice, no gui)
# --------------------------

class UI:

    """ constructor """
    def __init__(self):
        pass

    """ get_prompt """
    def get_prompt(self, prompt):    
        text = input(prompt) # ask the user to prompt
        return text

        
