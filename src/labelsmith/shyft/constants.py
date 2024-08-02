# src/labelsmith/shyft/constants.py
import appdirs
import logging
from pathlib import Path

logger = logging.getLogger("labelsmith")

APP_NAME = "Labelsmith"
APP_AUTHOR = "kosmolebryce"
APP_DATA_DIR = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR), "Shyft")
CONFIG_FILE = APP_DATA_DIR / "config.ini"
DATA_FILE_PATH = APP_DATA_DIR / "data.json"
LOGS_DIR = APP_DATA_DIR / "logs"