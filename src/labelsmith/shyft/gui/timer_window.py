import tkinter as tk
import configparser
from datetime import datetime, timedelta
import threading
import time
import logging
from labelsmith.shyft.constants import CONFIG_FILE

logger = logging.getLogger("labelsmith")

class TimerWindow:
    def __init__(self, root, time_color="#A78C7B", bg_color="#FFBE98"):
        self.root = root
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)

        if not self.config.has_section("Window"):
            self.config.add_section("Window")
            self.custom_width = 200
            self.custom_height = 100
            logger.debug(
                "No 'Window' section found in config file, using default dimensions."
            )
        else:
            self.custom_width = self.config.getint("Window", "width", fallback=200)
            self.custom_height = self.config.getint("Window", "height", fallback=100)
            logger.debug(
                f"Loaded custom dimensions from config file: width={self.custom_width}, height={self.custom_height}"
            )

        self.root.title("Timer")
        self.root.geometry(f"{self.custom_width}x{self.custom_height}")
        self.root.configure(bg=bg_color)

        self.elapsed_time = timedelta(0)
        self.running = False
        self.last_time = None
        self.time_color = time_color
        self.bg_color = bg_color

        self.timer_label = tk.Label(
            self.root,
            text="00:00:00",
            font=("Helvetica Neue", 32, "bold"),
            fg=self.time_color,
            bg=self.bg_color,
        )
        self.timer_label.pack(expand=True, padx=0, pady=(5, 0))

        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(fill="x", padx=10, pady=(0, 5))

        button_font = ("Helvetica", 10)
        self.start_button = tk.Button(
            button_frame,
            text="Start",
            command=self.start,
            bg=self.bg_color,
            fg=self.time_color,
            highlightbackground=self.bg_color,
            highlightthickness=0,
            bd=0,
            font=button_font,
        )
        self.start_button.grid(row=0, column=0, sticky="ew", padx=2)

        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop,
            bg=self.bg_color,
            fg=self.time_color,
            highlightbackground=self.bg_color,
            highlightthickness=0,
            bd=0,
            font=button_font,
        )
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=2)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset,
            bg=self.bg_color,
            fg=self.time_color,
            highlightbackground=self.bg_color,
            highlightthickness=0,
            bd=0,
            font=button_font,
        )
        self.reset_button.grid(row=0, column=2, sticky="ew", padx=2)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        self.update_timer_thread = threading.Thread(
            target=self.update_timer, daemon=True
        )
        self.update_timer_thread.start()
        logger.info("Timer window initialized.")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self):
        if not self.running:
            self.running = True
            self.last_time = datetime.now()
            logger.debug("Timer started.")

    def stop(self):
        if self.running:
            self.running = False
            self.elapsed_time += datetime.now() - self.last_time
            logger.debug("Timer stopped.")

    def reset(self):
        self.stop()
        self.elapsed_time = timedelta(0)
        self.update_label("00:00:00")
        logger.debug("Timer reset.")

    def update_label(self, text):
        if self.timer_label.winfo_exists():
            self.timer_label.config(text=text)

    def update_timer(self):
        while True:
            if self.running:
                current_time = datetime.now()
                delta = current_time - self.last_time
                elapsed = self.elapsed_time + delta
                self.root.after(
                    0, self.update_label, str(elapsed).split(".")[0].rjust(8, "0")
                )
            time.sleep(0.1)

    def on_close(self):
        self.running = False
        self.config.set("Window", "width", str(self.root.winfo_width()))
        self.config.set("Window", "height", str(self.root.winfo_height()))
        with open(CONFIG_FILE, "w") as config_file:
            self.config.write(config_file)
        logger.debug(
            f"Timer window dimensions saved: width={self.root.winfo_width()}, height={self.root.winfo_height()}"
        )
        self.root.after(0, self.root.destroy)
        logger.debug("Timer window closed.")