# src/screenshot.py

# This file manages the screenshot functionality for the Maths Online application.
# It captures screenshots of the question and answers regions based on the configuration settings.
# This file stores the screenshots in workspace/screenshots and deletes old screenshots if necessary.

from pathlib import Path
import pyautogui
from config import config
import random
import string
from .debug import log
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

answers_dir = screenshots / "answers"

random_letters = 12

answers_dir.mkdir(parents=True, exist_ok=True)
cache_dir.mkdir(parents=True, exist_ok=True)


def capture_screenshot():
    """
    Capture a screenshot of the question region as defined in the config.

    The screenshot is saved in the answers directory with a unique filename.
    If a generated filename already exists, a new one is generated.

    The screenshot is then saved in the workspace/answers directory.

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
    for path in [answers_dir]:
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


def optimize_image_for_openai(
    input_path, output_path=None, max_size=(600, 600), quality=60
):
    """
    Optimize an image to use the least amount of OpenAI tokens possible.
    This includes resizing, converting to JPEG, and compressing.
    The optimized image is saved to workspace/cache.

    Args:
        input_path (str or Path): Path to the input image file.
        output_path (str or Path, optional): Path to save the optimized image. If None, saves to cache.
        max_size (tuple): Maximum (width, height) for resizing.
        quality (int): JPEG quality (1-95, lower means more compression).

    Returns:
        Path: Path to the optimized image file in cache.
    """
    img = Image.open(input_path)
    img = img.convert("RGB")  # JPEG does not support transparency

    # Resize if larger than max_size
    img.thumbnail(max_size, Image.LANCZOS)

    # Save to cache_dir if output_path not specified
    if output_path is None:
        output_path = cache_dir / (Path(input_path).stem + ".jpg")
    else:
        output_path = Path(output_path)

    # Save as compressed JPEG
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    log(f"Image optimized and saved to {output_path}", "debug")

    return output_path


def encode_image_to_base64(image_path):
    """Encode an image file to a base64 string.

    Args:
        image_path (str or Path): Path to the image file."""
    import base64

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    log(f"Image encoded to base64 string of length {len(encoded_string)}", "debug")
    return encoded_string
