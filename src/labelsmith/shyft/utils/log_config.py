import logging
from pathlib import Path
from labelsmith.shyft.constants import LOGS_DIR

def configure_logging():
    # Create logs directory if it doesn't exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Basic configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOGS_DIR / "app.log"),
            logging.StreamHandler()
        ]
    )

    # Reduce logging level for some overly verbose libraries
    # logging.getLogger('matplotlib').setLevel(logging.WARNING)
    # logging.getLogger('PIL').setLevel(logging.WARNING)

    # You can add more library-specific logging configurations here