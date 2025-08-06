# config/__init__.py

# This file is used to initialize the config module. The configuration is found in config.yaml.
# It is highly recommended to edit the config.yaml file to suit your system's needs.
# Specifically if you do not have a 1920x1080 monitor, you should change the resolution settings.


# Program Imports
import yaml
from pathlib import Path
from dotenv import load_dotenv
import os

ENV_FILE = Path(__file__).parent / "secrets.env"
load_dotenv(dotenv_path=ENV_FILE)

CONFIG_FILE = Path(__file__).parent / "config.yaml"


def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)


config = load_config()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
