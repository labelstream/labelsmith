from datetime import datetime, timedelta
import logging

logger = logging.getLogger("labelsmith")

def validate_time_format(time_str: str) -> bool:
    """
    Validate the time string format (HH:MM).

    Args:
        time_str (str): The time string to validate.

    Returns:
        bool: True if the format is valid, False otherwise.

    Raises:
        ValueError: If the time format is invalid.
    """
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        logger.error(f"Invalid time format: {time_str}")
        raise ValueError("Invalid time format. Please use HH:MM format.")

def calculate_duration(start_time: str, end_time: str) -> float:
    """
    Calculate the duration between two time strings.

    Args:
        start_time (str): The start time in HH:MM format.
        end_time (str): The end time in HH:MM format.

    Returns:
        float: The duration in hours.
    """
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    duration = end - start
    if duration.total_seconds() < 0:
        duration += timedelta(days=1)
    
    return duration.total_seconds() / 3600

def format_to_two_decimals(value: float) -> str:
    """
    Format a float value to a string with two decimal places.

    Args:
        value (float): The value to format.

    Returns:
        str: The formatted string.
    """
    return f"{value:.2f}"