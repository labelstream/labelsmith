import logging
import tkinter as tk
import threading
from datetime import datetime
from labelsmith.shyft.gui.timer_window import TimerWindow
from labelsmith.shyft.gui.custom_widgets import CustomTooltip, DictionaryLookupText, IndependentAskString
from labelsmith.shyft.core.data_manager import data_manager
from labelsmith.shyft.utils.time_utils import calculate_duration, format_to_two_decimals
from labelsmith.shyft.utils.system_utils import prevent_sleep, allow_sleep, get_modifier_key
from labelsmith.shyft.constants import CONFIG_FILE, LOGS_DIR
from pathlib import Path
from tkinter import simpledialog, messagebox, ttk

logger = logging.getLogger("labelsmith")

class Autologger:
    def __init__(
        self,
        parent,
        timer_window,
        time_color,
        bg_color,
        btn_text_color,
        config,
        menu_bar,
        callback,
        tree):
        self.parent = parent
        self.parent.callback = callback
        self.parent.tree = tree
        self.timer_window = timer_window
        self.time_color = time_color
        self.bg_color = bg_color
        self.btn_text_color = btn_text_color
        self.config = config
        self.collected_data = []
        self.task_start_time = None
        self.caffeinate_process = None
        self.menu_bar = menu_bar

    def start(self):
        self.disable_theme_menu()
        shared_data = self.collect_shared_data()
        if shared_data is None:  # User cancelled
            return
        self.prevent_sleep()
        self.attempt_task(shared_data)


    def collect_shared_data(self):
        shared_fields = [
            ("Model ID", str.upper),
            ("Project ID", str.upper),
            ("Hourly Rate of Pay", float),
        ]

        shared_data = {}
        for field, transform in shared_fields:
            response = simpledialog.askstring(field, f"Enter {field}", parent=self.parent)
            if response is None:  # User clicked cancel
                return None
            try:
                shared_data[field] = transform(response)
            except ValueError:
                messagebox.showerror("Error", f"Invalid input for {field}")
                return None

        return shared_data

    def attempt_task(self, shared_data):
        if self.timer_window is None or not tk.Toplevel.winfo_exists(self.timer_window.root):
            self.timer_window = TimerWindow(tk.Toplevel(self.parent), time_color=self.time_color, bg_color=self.bg_color)
            self.timer_window.start()
            topmost_state = self.config.getboolean("Theme", "timer_topmost", fallback=False)
            self.timer_window.root.attributes("-topmost", topmost_state)
            self.enable_topmost_menu()

        self.task_start_time = datetime.now()

        # Create justification window
        justification_window = self.create_justification_window(shared_data)
        self.parent.wait_window(justification_window)

        if hasattr(justification_window, 'result'):
            if justification_window.result == "skipped":
                self.ask_attempt_another(shared_data)
            elif justification_window.result is not None:
                task_end_time = datetime.now()
                task_duration = task_end_time - self.task_start_time
                task_duration_str = f"{task_duration.seconds // 3600:02d}:{(task_duration.seconds % 3600) // 60:02d}"
                
                justification_window.result['Task Duration'] = task_duration_str
                
                self.collected_data.append(justification_window.result)
                self.ask_attempt_another(shared_data)
            else:
                self.finish_logging(cancel=True)
        else:
            self.finish_logging(cancel=True)

    def create_justification_window(self, shared_data):
        modkey = get_modifier_key()
    
        justification_window = tk.Toplevel(self.parent)
        justification_window.title("Rank and Justification")
        justification_window.geometry("500x500")
        justification_window.protocol("WM_DELETE_WINDOW", lambda: self.on_justification_close(justification_window))

        # Create a frame for task-specific data fields
        task_data_frame = ttk.Frame(justification_window)
        task_data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        task_fields = [
            ("Platform ID", str),
            ("Permalink", str),
            ("Response #1 ID", str),
            ("Response #2 ID", str)
        ]

        # Dictionary to store entry widgets
        task_entries = {}

        # Add labels and entry widgets to the grid
        for i, (field, transform) in enumerate(task_fields):
            label = ttk.Label(task_data_frame, text=f"Enter {field}:")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(task_data_frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            task_entries[field] = entry

        # Make the columns expand dynamically
        task_data_frame.columnconfigure(1, weight=1)

        # Rank selection
        rank_frame = ttk.Frame(justification_window)
        rank_frame.pack(fill=tk.X, padx=10, pady=5)
        rank_var = tk.StringVar()
        rank_options = [
            "(1) is much better than (2).",
            "(1) is slightly better than (2).",
            "The responses are of equal quality.",
            "(2) is slightly better than (1).",
            "(2) is much better than (1).",
            "Task rejected for containing unratable content."]
            
        ttk.Label(rank_frame, text="Rank:").pack(side=tk.LEFT)
        rank_dropdown = ttk.Combobox(rank_frame, textvariable=rank_var, values=rank_options, state="readonly", width=40)
        rank_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)
        rank_dropdown.set(rank_options[0])

        # Justification text box (using DictionaryLookupText)
        justification_frame = ttk.Frame(justification_window)
        justification_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(justification_frame, text="Justification:").pack(anchor="w")
        justification_text = DictionaryLookupText(justification_frame, wrap='word', height=10)
        justification_text.pack(fill=tk.BOTH, expand=True)

        # Bind keyboard shortcuts
        justification_window.bind(f"<{modkey}-w>", lambda event: self.on_justification_close(justification_window))
        justification_window.bind(f"<{modkey}-W>", lambda event: self.on_justification_close(justification_window))

        def submit_data():
            justification_window.result = shared_data.copy()
            for field, entry in task_entries.items():
                try:
                    justification_window.result[field] = entry.get()
                except ValueError:
                    messagebox.showerror("Error", f"Invalid input for {field}")
                    return
            justification_window.result['Rank'] = rank_var.get()
            justification_window.result['Justification'] = justification_text.get("1.0", tk.END).strip()
            justification_window.destroy()

        def skip_task():
            justification_window.result = "skipped"
            justification_window.destroy()

        # Buttons
        button_frame = ttk.Frame(justification_window)
        button_frame.pack(fill=tk.X, pady=10)
        submit_button = ttk.Button(button_frame, text="Submit", command=submit_data)
        submit_button.pack(side=tk.RIGHT, padx=5)
        skip_button = ttk.Button(button_frame, text="Skip", command=skip_task)
        skip_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=lambda: self.on_justification_close(justification_window))
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # Set focus to the first entry widget
        first_entry = next(iter(task_entries.values()))
        first_entry.focus_set()

        justification_window.focus_set()
        return justification_window
    
    def on_justification_close(self, window):
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel? This will end the current shift logging process."):
            window.result = None  # Set result to None to indicate cancellation
            window.destroy()
        # If 'No' is selected, do nothing and keep the window open

    def ask_attempt_another(self, shared_data):
        response = messagebox.askyesno(
            "Attempt Another Task", "Would you like to attempt another task?"
        )
        if response:
            self.attempt_task(shared_data)
        else:
            self.finish_logging()

    def finish_logging(self, cancel=False):
        try:
            if cancel or not self.collected_data:
                if cancel:
                    messagebox.showinfo("Cancelled", "Autologger process cancelled.")
            else:
                shift_id = self.log_shift()
                if shift_id:
                    self.save_shift_markdown(shift_id)
        finally:
            # Always perform these cleanup actions
            if self.timer_window and tk.Toplevel.winfo_exists(self.timer_window.root):
                self.timer_window.reset()
                self.timer_window.on_close()
                self.timer_window = None

        self.allow_sleep()  # Ensure caffeinate is terminated when the app quits
        self.parent.grab_set()
        self.parent.tree.focus_set()
        self.parent.callback()

    def save_shift_markdown(self, shift_id: str):
        markdown_content = self.create_shift_markdown(shift_id)
        logs_dir = Path(LOGS_DIR)
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_path = logs_dir / f"{shift_id}.md"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Shift log saved: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save shift log: {e}")

    def log_shift(self):
        if self.timer_window and tk.Toplevel.winfo_exists(self.timer_window.root):
            self.timer_window.stop()
            elapsed_time = self.timer_window.elapsed_time

            duration_hrs = elapsed_time.total_seconds() / 3600

            gross_pay = duration_hrs * self.collected_data[0]["Hourly Rate of Pay"]

            new_id = data_manager.get_max_shift_id() + 1
            formatted_id = f"{new_id:04d}"

            tasks_completed = len(self.collected_data)

            task_durations = {
                str(i): {"Duration (hh:mm)": task_data['Task Duration']}
                for i, task_data in enumerate(self.collected_data, start=1)
            }

            shift_data = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Model ID": self.collected_data[0]["Model ID"],
                "Project ID": self.collected_data[0]["Project ID"],
                "In (hh:mm)": (datetime.now() - elapsed_time).strftime("%H:%M"),
                "Out (hh:mm)": datetime.now().strftime("%H:%M"),
                "Duration (hrs)": format_to_two_decimals(duration_hrs),
                "Hourly rate": format_to_two_decimals(self.collected_data[0]['Hourly Rate of Pay']),
                "Gross pay": format_to_two_decimals(gross_pay),
                "Tasks completed": tasks_completed,
                "Task durations": task_durations
            }

            data_manager.add_shift(formatted_id, shift_data)
            messagebox.showinfo(
                "Success",
                f"Shift logged successfully. {tasks_completed} tasks completed.",
            )
            logger.info(
                f"Shift logged successfully. {tasks_completed} tasks completed."
            )

            return formatted_id
        else:
            messagebox.showerror("Error", "Timer is not running.")
            logger.error("Failed to log shift: Timer is not running.")
            return None

        if self.timer_window and tk.Toplevel.winfo_exists(self.timer_window.root):
            self.timer_window.reset()
            self.timer_window.on_close()
            self.timer_window = None
            self.enable_theme_menu()
            self.disable_topmost_menu()
        
    def create_shift_markdown(self, shift_id: str) -> str:
        markdown_content = f"""# `{shift_id}.md`

----
"""
        for i, task_data in enumerate(self.collected_data, start=1):
            markdown_content += f"""

{i}. `{task_data['Platform ID']}`

[Permalink]
{task_data['Permalink']}

[Response IDs]
1. {task_data['Response #1 ID']}
2. {task_data['Response #2 ID']}

[Rank]
{task_data['Rank']}

[Justification]
{task_data['Justification']}

"""
        return markdown_content

    def prevent_sleep(self):
        self.caffeinate_process = prevent_sleep(self)

    def allow_sleep(self):
        allow_sleep(self.caffeinate_process)
        self.caffeinate_process = None

    def disable_theme_menu(self):
        self.menu_bar.entryconfig("Theme", state="disabled")

    def enable_theme_menu(self):
        self.menu_bar.entryconfig("Theme", state="normal")

    def enable_topmost_menu(self):
        self.menu_bar.entryconfig("View", state="normal")

    def disable_topmost_menu(self):
        self.menu_bar.entryconfig("View", state="disabled")