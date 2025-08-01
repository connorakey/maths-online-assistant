# src/debug.py
# This module provides debugging utilities for the Maths Online application.
# It includes a logging function that writes debug messages to a log file.

from pathlib import Path
from datetime import datetime
from config import config
import random
import string


workspace = Path("workspace")
logs = workspace / "logs"


def random_letter_string(num: int):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(num))


file_name = (
    f"debug-{datetime.now().strftime('%Y-%m-%d')}-{random_letter_string(12)}.log"
)

logs.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str):
    if level not in ["debug", "minimal"]:
        raise ValueError("Invalid log level. Use 'debug' or 'minimal'.")

    if not config["debug"]["enabled"]:
        return

    log_file = logs / file_name

    if config["debug"]["level"] == "minimal" and level == "minimal":
        with log_file.open("a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} [{level}] {message}\n")
            print(f"{timestamp} [{level}] {message}")
    elif config["debug"]["level"] == "debug":
        with log_file.open("a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} [{level}] {message}\n")
            print(f"{timestamp} [{level}] {message}")


def clear_all_logs():
    success = True
    for path in [logs]:
        if not path.exists() or not path.is_dir():
            log(f"Path {path} does not exist or is not a directory.", "minimal")
            continue

        for file_path in path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".log":
                try:
                    file_path.unlink()
                    log(f"Deleted file: {file_path}", "debug")
                except Exception as e:
                    log(f"Error deleting file {file_path}: {e}", "debug")
                    success = False
            else:
                log(f"Skipping file: {file_path}", "debug")
    return success
