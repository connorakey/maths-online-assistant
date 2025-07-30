# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

# TODO:
# Add debug functionality to this script, possibily with an external python script like debug.py replace the commented print functions with logging.


from pathlib import Path
import pyautogui
from config import config
import random
import string

def random_letter_string(num: int):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(num))

workspace = Path("workspace")
screenshots = workspace / "screenshots"

questions_dir = screenshots / "questions"
answers_dir = screenshots / "answers"

random_letters = 12

questions_dir.mkdir(parents=True, exist_ok=True)
answers_dir.mkdir(parents=True, exist_ok=True)


def capture_screenshot():

    points = config["ui"]["question_region"]
    #print(f"Captures points from config {points}")

    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    width = max_x - min_x
    height = max_y - min_y

    screenshot = pyautogui.screenshot(region=(min_x, min_y, width, height))

        
    filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"
    #print(f"Generated file name: {filename}")

    while True:
        if check_if_exists(answers_dir, filename):
            #print(f"Filename: {filename} exists, randomly generating another file name.")
            filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"
            #print(f"Generated file name: {filename}")
        else:
            #print("File name does not exist.")
            save_path = answers_dir / filename
            screenshot.save(save_path)
            #print("Screenshot saved.")
            break

    
    
    return filename

def check_if_exists(path: str, filename: str):
    file_path = path / filename
    if file_path.exists() and file_path.is_file():
        return True
    else:
        return False

def clear_all_screenshots():
    success = True
    for path in [questions_dir, answers_dir]:
        if not path.exists() or not path.is_dir():
            #print(f"Path {path} does not exist or is not a directory.")
            continue

        for file_path in path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".png":
                try:
                    file_path.unlink()
                    #print(f"Deleted file: {file_path}")
                except Exception as e:
                    #print(f"Error deleting file {file_path}: {e}")
                    success = False
            #else:
                #print(f"Skipping file: {file_path}")
    return success
