# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

from pathlib import Path
import pyautogui
from config import config
import random
import string
from src.debug import log
from PIL import Image


def random_letter_string(num: int):
    """
    Generate a random string of ASCII letters of length `num`.

    Args:
        num (int): The length of the string to generate.

    Returns:
        str: A random string of ASCII letters.
    """
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(num))


workspace = Path("workspace")
cache_dir = workspace / "cache"
screenshots = workspace / "screenshots"

questions_dir = screenshots / "questions"
answers_dir = screenshots / "answers"

random_letters = 12

questions_dir.mkdir(parents=True, exist_ok=True)
answers_dir.mkdir(parents=True, exist_ok=True)


def capture_screenshot():
    """
    Capture a screenshot of the question region as defined in the config.

    The screenshot is saved in the answers directory with a unique filename.
    If a generated filename already exists, a new one is generated.

    Returns:
        str: The filename of the saved screenshot.
    """
    points = config["ui"]["question_region"]
    log(f"Captures points from config {points}", "debug")

    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    width = max_x - min_x
    height = max_y - min_y

    screenshot = pyautogui.screenshot(region=(min_x, min_y, width, height))

    filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"
    log(f"Generated file name: {filename}", "debug")

    while True:
        if check_if_exists(answers_dir, filename):
            log(
                f"Filename: {filename} exists, randomly generating another file name.",
                "debug",
            )
            filename = f"mathsonline-answer-{random_letter_string(random_letters)}.png"
            log(f"Generated file name: {filename}", "debug")
        else:
            log("File name does not exist.", "debug")
            save_path = answers_dir / filename
            screenshot.save(save_path)
            log("Screenshot saved.", "debug")
            break

    return filename


def compress_screenshot(filename: str, quality: int = 60):
    """
    Compress a screenshot file to reduce its size and move it to the cache directory.

    Args:
        filename (str): The filename of the screenshot to compress.
        quality (int): JPEG quality (1-95, higher is better quality).

    Returns:
        str: The new compressed filename.
    """
    file_path = answers_dir / filename
    img = Image.open(file_path)
    compressed_filename = filename.replace(".png", ".jpg")
    compressed_path = cache_dir / compressed_filename
    img = img.convert("RGB")  # JPEG does not support transparency
    img.save(compressed_path, "JPEG", quality=quality, optimize=True)
    return


def check_if_exists(path: str, filename: str):
    """
    Check if a file exists at the given path with the specified filename.

    Args:
        path (str or Path): The directory path.
        filename (str): The filename to check.

    Returns:
        bool: True if the file exists and is a file, False otherwise.
    """
    file_path = path / filename
    if file_path.exists() and file_path.is_file():
        return True
    else:
        return False


def clear_all_screenshots():
    """
    Delete all PNG screenshot files in the questions and answers directories.

    Returns:
        bool: True if all deletions succeeded, False if any deletion failed.
    """
    success = True
    for path in [questions_dir, answers_dir]:
        if not path.exists() or not path.is_dir():
            log(f"Path {path} does not exist or is not a directory.", "minimal")
            continue

        for file_path in path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".png":
                try:
                    file_path.unlink()
                    log(f"Deleted file: {file_path}", "debug")
                except Exception as e:
                    log(f"Error deleting file {file_path}: {e}", "debug")
                    success = False
            else:
                log(f"Skipping file: {file_path}", "debug")
    return success
