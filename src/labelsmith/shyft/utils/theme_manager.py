import tkinter as tk
from tkinter import ttk
import logging
from labelsmith.shyft.core import config_manager

config = config_manager.load_config()
logger = logging.getLogger("labelsmith")

class ThemeManager:
    @staticmethod
    def change_theme(style: ttk.Style, theme_name: str) -> None:
        """
        Change the application theme.

        Args:
            style (ttk.Style): The ttk Style object.
            theme_name (str): The name of the theme to apply.
        """
        try:
            style.theme_use(theme_name)
            config.set("Theme", "selected", theme_name)
            save_config(config)
            logger.info(f"Theme changed to: {theme_name}")
        except tk.TclError as e:
            logger.error(f"Failed to change theme: {e}")

    @staticmethod
    def get_available_themes(style: ttk.Style) -> list:
        """
        Get a list of available themes.

        Args:
            style (ttk.Style): The ttk Style object.

        Returns:
            list: A list of available theme names.
        """
        return style.theme_names()

    @staticmethod
    def update_color_scheme(gui, color_type: str, color_code: str) -> None:
        """
        Update the color scheme of the application.

        Args:
            gui: The main GUI object.
            color_type (str): The type of color to update (e.g., 'time_color', 'bg_color').
            color_code (str): The new color code.
        """
        try:
            setattr(gui, color_type, color_code)
            config.set("Colors", color_type, color_code)
            save_config(config)
            logger.info(f"Updated {color_type} to: {color_code}")
            if gui.timer_window:
                gui.reinitialize_timer_window()
        except Exception as e:
            logger.error(f"Failed to update color scheme: {e}")