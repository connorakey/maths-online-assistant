# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

# TODO:
# Add debug functionality to this script, possibily with an external python script like debug.py
# Implement deletion of old screenshot folders

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

    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    width = max_x - min_x
    height = max_y - min_y

    screenshot = pyautogui.screenshot(region=(min_x, min_y, width, height))

        
    filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"

    while True:
        if check_if_exists(answers_dir, filename):
            filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"
        else:
            save_path = answers_dir / filename
            screenshot.save(save_path)
            break

    
    
    return filename

def check_if_exists(path: str, filename: str):
    file_path = path / filename
    if file_path.exists() and file_path.is_file():
        return True
    else:
        return False

capture_screenshot()