import sys
import time
import json
import argparse
import pyperclip
import subprocess

from lebon.constants import JSON_FILE
from lebon.utils import gemini_answers, modify_env, is_api_present


def main():
    parser = argparse.ArgumentParser(description="hey wassup lol :3")
    parser.add_argument("-r", "--reset", action="store_true", help="reset api key.")

    args = parser.parse_args()

    if not any(vars(args).values()):
        try:
            if not is_api_present():
                api_key = str(input("Gemini API key: "))
                
                if len(api_key) < 38:
                    print("Invalid API key.")
                    sys.exit(0)

                with open(JSON_FILE, "r") as file:
                    data = json.load(file)
                    
                data["GOOGLE_API_KEY"] = api_key.strip()
                
                with open(JSON_FILE, "w") as file:
                    json.dump(data, file)
                    
                print("API key saved successfully.")
                subprocess.run(["lebon"])
                
            else:
                _ = modify_env(True)

                while True:
                    try:
                        user_input = str(input("ඞ"))
                        print("\033[H\033[J")
                        
                        if user_input == "":
                            clipboard_content = pyperclip.paste()
                            
                            if len(clipboard_content.strip(" "))<1:
                                print("Clipboard is empty.")
                                continue    
                    
                            answers = gemini_answers(clipboard_content)
                            print(answers.replace('\n\n', '\n'))
                            time.sleep(3)
                            print("\033[H\033[J")

                        elif user_input == "exit":
                            modify_env(transparent=False)
                            sys.exit(0)
                        elif user_input == "cls" or user_input == "clear":
                            print("\033[H\033[J")
                            
                        # else:
                        #     break
                        
                    except KeyboardInterrupt:
                        modify_env(transparent=False)
                        sys.exit(0)

                    except Exception as e:
                        print(f"Error: {e}")
                        continue
                        
        except KeyboardInterrupt:
            modify_env(transparent=False)
            sys.exit(0)
            
    elif args.reset:
        with open(JSON_FILE, "r") as file: data = json.load(file)
        data["GOOGLE_API_KEY"] = ""
        with open(JSON_FILE, "w") as file: json.dump(data, file)
            
        print("API key reset successfully.")
        subprocess.run(["lebon"])


if __name__ == "__main__":
    main()