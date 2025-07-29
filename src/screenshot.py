# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

# TODO:
# Add debug functionality to this script, possibily with an external python script like debug.py
# Implement deletion of old screenshot folders
# Check if file exists, so errors don't occur

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


def capture_question_screenshot():
    question_region = config["ui"]["question_region"]
    screenshot = pyautogui.screenshot(region=question_region)

    filename = f"mathsonline-question-{random_letter_string(random_letters)}.png"

    save_path = questions_dir / filename
    screenshot.save(save_path)

    return filename


def capture_answers_screenshot():
    answer_region = config["ui"]["answers_region"]
    screenshot = pyautogui.screenshot(region=answer_region)

    filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"

    save_path = answers_dir / filename
    screenshot.save(save_path)
    
    return filename