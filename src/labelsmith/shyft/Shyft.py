import multiprocessing
import tkinter as tk
import logging
from labelsmith.shyft.gui.main_window import ShyftGUI
from labelsmith.shyft.utils.system_utils import get_modifier_key, modkey_backspace, modkey_shift_backspace
from labelsmith.shyft.core.nltk_manager import initialize_nltk
from labelsmith.shyft.utils.log_config import configure_logging
from labelsmith.shyft.constants import APP_AUTHOR, APP_DATA_DIR, APP_NAME, DATA_FILE_PATH, CONFIG_FILE, LOGS_DIR

logger = configure_logging()

def run_tkinter_app():
    root = tk.Tk()
    app = ShyftGUI(root)
    modkey = get_modifier_key()

    shortcuts = {
        "a": app.autologger,
        "d": app.delete_shift,
        "e": app.edit_shift,
        "n": app.manual_entry,
        "l": app.view_logs,
        "t": app.calculate_totals,
        "q": app.on_quit,
    }

    for key, func in shortcuts.items():
        root.bind(f"<{modkey}-{key}>", func)
        root.bind(f"<{modkey}-{key.upper()}>", func)

    # Modify these lines to handle both shift keys
    root.bind_all(f"<{modkey}-BackSpace>", modkey_backspace)
    root.bind_all(f"<{modkey}-Shift-BackSpace>", modkey_shift_backspace)
    root.bind_all(f"<{modkey}-Shift-BackSpace>", modkey_shift_backspace, add='+')

    root.bind_all(f"<{modkey}-m>", app.minimize_window)

    root.mainloop()

def main():
    configure_logging()
    
    try:
        nltk_available = initialize_nltk()
    except Exception as e:
        logger.error(f"Failed to initialize NLTK: {e}")
        nltk_available = False
    
    process = multiprocessing.Process(target=run_tkinter_app)
    process.start()
    logger.info(f"Application started. NLTK WordNet available: {nltk_available}")
    logger.info(f"""
`APP_NAME`: {APP_NAME}
`APP_AUTHOR`: {APP_AUTHOR}
`APP_DATA_DIR`: {APP_DATA_DIR}
`CONFIG_FILE`: {CONFIG_FILE}
`DATA_FILE_PATH`: {DATA_FILE_PATH}
`LOGS_DIR`: {LOGS_DIR}
"""
)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()