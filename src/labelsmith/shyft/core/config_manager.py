import configparser
import logging
from labelsmith.shyft.constants import CONFIG_FILE

logger = logging.getLogger("labelsmith")

def load_config():
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
        logger.debug(f"Configuration loaded from {CONFIG_FILE}")
    else:
        logger.warning(f"Configuration file {CONFIG_FILE} does not exist. Using default settings.")
    
    # Add default tax rate if it doesn't exist
    if 'Settings' not in config:
        config['Settings'] = {}
    if 'tax_rate' not in config['Settings']:
        config['Settings']['tax_rate'] = '0.27'
    
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)