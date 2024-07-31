import configparser
import logging
from labelsmith.shyft.constants import CONFIG_FILE

logger = logging.getLogger(__name__)

def load_config():
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
        logger.debug(f"Configuration loaded from {CONFIG_FILE}")
    else:
        logger.warning(f"Configuration file {CONFIG_FILE} does not exist. Using default settings.")
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)