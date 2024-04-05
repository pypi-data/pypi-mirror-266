import os
import json
import pkg_resources


LOCALAPP_DATA = os.getenv('LOCALAPPDATA')
PACKAGE_PATH = os.path.join(LOCALAPP_DATA, 'Packages', 'Microsoft.WindowsTerminal_8wekyb3d8bbwe')
SETTINGS_PATH = os.path.join(PACKAGE_PATH, 'LocalState', 'settings.json')

JSON_FILE = pkg_resources.resource_filename('lebon', 'assets/data.json')

INSTRUCTIONS = """
I am going to pass you a few MCQ questions. Your job is to identify the questions and respond with just the correct answer and the answer text: 

Here is an example for what I am expecting:
Q1. B) Waltuh

Note: 
1. In case you cannot identify the questions, you can respond with 'Please paste the questions again.'
2. Strictly do not give any sort of explanation.

Your questions are as follows:
"""

with open(JSON_FILE, "r") as file:
    data = json.load(file)
    
GOOGLE_API_KEY = data.get("GOOGLE_API_KEY")