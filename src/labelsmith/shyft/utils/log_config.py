import logging
from pathlib import Path
from labelsmith.shyft.constants import (
    APP_NAME, APP_AUTHOR, APP_DATA_DIR,
    CONFIG_FILE, DATA_FILE_PATH, LOGS_DIR
    )

def configure_logging():
    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger('labelsmith')
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

    # Create handlers
    file_handler = logging.FileHandler(LOGS_DIR / "app.log")
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Console shows INFO and above

    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent logger from passing messages to the root logger
    logger.propagate = False

    # Reduce logging level for some overly verbose libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    return logger