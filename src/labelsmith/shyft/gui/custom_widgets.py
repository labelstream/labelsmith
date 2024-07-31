import tkinter as tk
from tkinter import ttk
import re
import platform
from nltk.corpus import wordnet

class CustomTooltip:
    def __init__(self, widget, text, close_callback):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.close_callback = close_callback

    def show(self):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#FFFFD0", fg="black",
                         relief='solid', borderwidth=1,
                         font=("TkDefaultFont", 10),
                         padx=5, pady=5)
        label.pack(ipadx=1)

        # Set a black border around the tooltip
        tw.configure(background="black")
        label.pack(padx=1, pady=1)

        # Make the tooltip focusable
        tw.focusmodel('active')
        tw.grab_set()
        tw.focus_set()

        # Bind click event to close the tooltip
        tw.bind("<Button-1>", self.on_click)

        # Bind the tooltip window's close event
        tw.protocol("WM_DELETE_WINDOW", self.hide)

    def hide(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.grab_release()
            self.tooltip_window.destroy()
        self.tooltip_window = None
        if self.close_callback:
            self.close_callback()

    def on_click(self, event):
        self.hide()

class DictionaryLookupText(tk.Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.tooltip = None
        self.tooltip_word = None

        # Determine the correct modifier key based on the operating system
        self.modifier = "Command" if platform.system() == "Darwin" else "Control"

        # Bind the key combination
        self.bind(f"<{self.modifier}-period>", self.toggle_definition)

    def toggle_definition(self, event):
        if self.tooltip:
            self.hide_tooltip()
        else:
            try:
                selected_text = self.selection_get().strip()
                word = strip_ansi_codes(selected_text).lower()
                if word:
                    self.show_definition(word)
            except tk.TclError:
                # No text selected
                pass
        return "break"  # Prevent the event from propagating

    def show_definition(self, word):
        try:
            definition = self.get_definition(word)
            synonyms = self.get_synonyms(word)

            tooltip_text = f"Definition: {definition}\n\nSynonyms: {', '.join(synonyms)}"
            self.create_tooltip(word, tooltip_text)
        except Exception as e:
            self.create_tooltip(word, f"An error occurred: {str(e)}")

    def get_definition(self, word):
        synsets = wordnet.synsets(word)
        if synsets:
            return synsets[0].definition()
        return "No definition found."

    def get_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().replace('_', ' '))
        return list(synonyms)[:5] if synonyms else ["No synonyms found."]

    def create_tooltip(self, word, tooltip_text):
        if self.tooltip:
            self.hide_tooltip()
        self.tooltip = CustomTooltip(self, tooltip_text, self.on_tooltip_close)
        self.tooltip_word = word
        self.tooltip.show()
        
        if self.tooltip.tooltip_window:
            self.tooltip.tooltip_window.attributes('-topmost', True)
            
            # Bind the modifier-period combination to close the tooltip
            self.tooltip.tooltip_window.bind(f"<{self.modifier}-period>", self.hide_tooltip)
            
            # Bind the escape key to close the tooltip
            self.tooltip.tooltip_window.bind("<Escape>", self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.hide()

    def on_tooltip_close(self):
        self.tooltip = None
        self.tooltip_word = None
        self.focus_set()

class IndependentAskString(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)
        self.result = None

        self.geometry("300x150")
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding="20 20 20 0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=prompt).pack(pady=(0, 10))
        self.entry = ttk.Entry(main_frame, width=40)
        self.entry.pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.grid(row=0, column=0, padx=(0, 5), sticky='e')
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).grid(row=0, column=1, padx=(5, 0), sticky='w')

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Center the dialog on the screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

        # Bind Enter key to OK button
        self.bind('<Return>', lambda event: ok_button.invoke())

        self.entry.focus_set()
        self.grab_set()
        self.wait_window()

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
