import os
import time
import json
import pkg_resources
import pyautogui as pg
import google.generativeai as genai
from lebon.constants import SETTINGS_PATH, GOOGLE_API_KEY, JSON_FILE


genai.configure(api_key=GOOGLE_API_KEY)

def path_convertor(path: str) -> str:
        try:
            return pkg_resources.resource_filename('lebon', path)
        except FileNotFoundError and ModuleNotFoundError:
            return path


def set_terminal_opacity(transparent: bool = True) -> str:
    print(f"{'Restoring' if not transparent else 'Modifying'} terminal opacity...")
    
    opacity_value = 0 if transparent else 100
    
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r') as f:
                settings_content = json.load(f)
            
            if "opacity" not in settings_content["profiles"]["defaults"]:
                settings_content["profiles"]["defaults"]["opacity"] = opacity_value
                with open(SETTINGS_PATH, "w") as file: 
                    json.dump(settings_content, file)
                return "Opacity appended successfully."
                
            opacity = int(settings_content["profiles"]["defaults"]["opacity"])
            
            if opacity != opacity_value:
                settings_content["profiles"]["defaults"]["opacity"] = opacity_value
                with open(SETTINGS_PATH, "w") as file: 
                    json.dump(settings_content, file)
                return "Opacity updated successfully."
            else:
                return "Opacity already set to the desired value."
        else:
            return "Settings file not found."
        
    except Exception as e:
        return f"An exception occurred: {e}"


def modify_env(transparent: bool = True) -> None:
    set_terminal_opacity(transparent)
    
    print("\033[H\033[J")
    
    if transparent:
        pg.press('f11')
        time.sleep(0.05)
        pg.hotkey('fn', 'f11')
        time.sleep(0.05)
        pg.press('f11')
    else:
        pg.press('f11')
    
    print("\033[H\033[J")


def is_api_present() -> bool:
    try:
        with open(JSON_FILE, "r") as file:
            data = json.load(file)
        api_key = data.get("GOOGLE_API_KEY")
        return False if api_key=="" else api_key
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def gemini_answers(question_string: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(question_string)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__=="__main__":
    while 1:
        set_terminal_opacity(transparent=True)
        time.sleep(2)
        set_terminal_opacity(transparent=False)
        time.sleep(2)