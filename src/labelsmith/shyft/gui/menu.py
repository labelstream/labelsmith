import tkinter as tk
from tkinter import colorchooser, ttk, messagebox
from labelsmith.shyft.core import config_manager
from labelsmith.shyft.core.config_manager import load_config, save_config
from labelsmith.shyft.utils.plotting import Plotting

plotter = Plotting ()
config = load_config()

def setup_menu(gui):
    gui.menu_bar = tk.Menu(gui.root)
    setup_file_menu(gui)
    setup_theme_menu(gui)
    setup_view_menu(gui)
    setup_settings_menu(gui)
    gui.root.config(menu=gui.menu_bar)

def setup_file_menu(gui):
    gui.file_menu = tk.Menu(gui.menu_bar, tearoff=0)
    gui.file_menu.add_command(label="Plot productivity", command=plotter.plot_productivity_default)
    # gui.file_menu.add_command(label="Plot productivity...", command=lambda: Plotting.plot_productivity_custom())
    gui.menu_bar.add_cascade(label="File", menu=gui.file_menu)

def setup_theme_menu(gui):
    gui.theme_menu = tk.Menu(gui.menu_bar, tearoff=0)
    themes = ["default", "classic", "alt", "clam"]
    for theme in themes:
        gui.theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: change_theme(gui, t))
    if gui.root.tk.call("tk", "windowingsystem") == "aqua":
        gui.theme_menu.add_command(label="Aqua", command=lambda: change_theme(gui, "aqua"))
    gui.menu_bar.add_cascade(label="Theme", menu=gui.theme_menu)
    enable_theme_menu(gui, gui.theme_menu)

def setup_view_menu(gui):
    gui.view_menu = tk.Menu(gui.menu_bar, tearoff=0)
    gui.view_menu.add_checkbutton(
        label="Timer Always on Top",
        command=gui.toggle_timer_topmost,
        variable=gui.timer_topmost_var,
    )
    gui.menu_bar.add_cascade(label="View", menu=gui.view_menu)

def setup_settings_menu(gui):
    gui.settings_menu = tk.Menu(gui.menu_bar, tearoff=0)
    gui.settings_menu.add_command(label="Stopclock Timestring Color", command=lambda: choose_color(gui, "time_color"))
    gui.settings_menu.add_command(label="Stopclock Background Color", command=lambda: choose_color(gui, "bg_color"))
    gui.settings_menu.add_command(label="Stopclock Button Text Color", command=lambda: choose_color(gui, "btn_text_color"))
    gui.menu_bar.add_cascade(label="Settings", menu=gui.settings_menu)

def change_theme(gui, theme_name):
    gui.style.theme_use(theme_name)
    config.set("Theme", "selected", theme_name)
    save_config(config)

def choose_color(gui, color_type):
    color_code = colorchooser.askcolor(title=f"Choose {color_type.replace('_', ' ').title()}")[1]
    if color_code:
        setattr(gui, color_type, color_code)
        config.set("Colors", color_type, color_code)
        save_config(config)
        if gui.timer_window:
            gui.reinitialize_timer_window()

def enable_topmost_menu(gui, view_menu):
    gui.view_menu.entryconfig("Timer Always on Top", state="normal")

def disable_topmost_menu(gui, view_menu):
    gui.view_menu.entryconfig("Timer Always on Top", state="disabled")

def disable_theme_menu(gui, theme_menu):
    gui.menu_bar.entryconfig("Theme", state="disabled")

def enable_theme_menu(gui, theme_menu):
    gui.menu_bar.entryconfig("Theme", state="normal")
