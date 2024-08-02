import os
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger("labelsmith")

def get_log_files(log_dir: Path) -> List[str]:
    """
    Get a list of log files in the specified directory.

    Args:
        log_dir (Path): The directory containing log files.

    Returns:
        List[str]: A list of log file names, sorted in reverse chronological order.
    """
    try:
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.md')]
        log_files = sorted(log_files, reverse=True)
        log_files.append("app.log")
        return log_files
    except FileNotFoundError:
        logger.error(f"Log directory not found: {log_dir}")
        return []
    except PermissionError:
        logger.error(f"Permission denied when accessing log directory: {log_dir}")
        return []
    except Exception as e:
        logger.error(f"Error while getting log files: {e}")
        return []