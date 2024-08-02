import nltk
from nltk.corpus import wordnet
from pathlib import Path
import logging
from labelsmith.shyft.constants import APP_DATA_DIR

logger = logging.getLogger("labelsmith")

def ensure_nltk_data():
    nltk_data_path = APP_DATA_DIR / "nltk_data"
    nltk.data.path.append(str(nltk_data_path))
    logger.debug(f"NLTK data path: {nltk.data.path}")

    if not nltk_data_path.exists():
        try:
            nltk.download("wordnet", download_dir=nltk_data_path)
            logger.info("WordNet data downloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download or extract WordNet data: {e}")
            return False

    # Verify that WordNet can be loaded
    try:
        wordnet.synsets('test')
        logger.info("WordNet data loaded successfully.")
        return True
    except LookupError as e:
        logger.error(f"WordNet data not found or corrupted: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading WordNet: {e}")
        return False

def initialize_nltk():
    if ensure_nltk_data():
        logger.info("NLTK WordNet is ready for use.")
        return True
    else:
        logger.warning("NLTK WordNet is not available. Dictionary feature will be disabled.")
        return False