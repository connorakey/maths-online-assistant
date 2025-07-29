# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

from pathlib import Path
import pyautogui
from config import config

workspace = Path("workspace")
screenshots = workspace / "screenshots"


def capture_question_screenshot(filename: str):
    question_region = config["ui"]["question_region"]

    print("Question region is", question_region)


def capture_answers_screenshot(filename: str):
    return
