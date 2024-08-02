import logging
import traceback
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger("labelsmith")

def error_handler(func: Callable) -> Callable:
    """
    A decorator for handling exceptions in functions.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper

def log_exception(e: Exception, context: str = "") -> None:
    """
    Log an exception with optional context.

    Args:
        e (Exception): The exception to log.
        context (str, optional): Additional context for the error. Defaults to "".
    """
    error_message = f"{context + ': ' if context else ''}{str(e)}"
    logger.error(error_message)
    logger.debug(f"Traceback: {traceback.format_exc()}")