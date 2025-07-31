import os
import random
import string
from datetime import datetime
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if 'config' in config:
        return config['config']
    return config

_config = load_config()
LOG_LEVEL = _config.get('debug', {}).get('log_level', 'debug').lower()

LOG_LEVELS = {
    'none': 0,
    'minimal': 1,
    'debug': 2
}

def get_log_level():
    return LOG_LEVELS.get(LOG_LEVEL, 2)

def generate_log_filename():
    now = datetime.now()
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"{now.year}-{now.month:02d}-{now.day:02d}-DEBUG-LOG-{rand_str}.txt"

LOG_FILENAME = generate_log_filename()
LOG_FILEPATH = os.path.join(".", LOG_FILENAME)

def log(message: str, level: str = "debug"):
    level = level.lower()
    current_level = get_log_level()

    # Only log if the message level is allowed by config
    if level == "minimal" and current_level >= 1:
        _write_log(message)
    elif level == "debug" and current_level >= 2:
        _write_log(message)
    # If log_level is 'none', nothing is logged

def _write_log(message: str):
    now = datetime.now()
    timestamp = f"{now.year}-{now.month:02d}-{now.day:02d}-{now.minute:02d}-{now.second:02d}"
    with open(LOG_FILEPATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}: {message}\n")