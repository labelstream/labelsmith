import tkinter as tk
from tkinter import ttk, messagebox
from labelsmith.shyft.core.data_manager import data_manager
from labelsmith.shyft.utils.file_utils import get_log_files
from labelsmith.shyft.utils.system_utils import get_modifier_key
from labelsmith.shyft.gui.custom_widgets import DictionaryLookupText
from labelsmith.shyft.constants import CONFIG_FILE, LOGS_DIR
import os
from pathlib import Path


class ViewLogsDialog:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("View Logs")
        self.window.geometry("480x640")
        self.create_widgets()
        self.window.bind(f"<{get_modifier_key()}-w>", self.close_window)
        self.window.bind(f"<{get_modifier_key()}-W>", self.close_window)

    def create_widgets(self):
        tree_frame = ttk.Frame(self.window)
        tree_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.log_tree = ttk.Treeview(tree_frame, columns=["Log Files"], show="headings", height=4)
        self.log_tree.heading("Log Files", text="Log Files")
        self.log_tree.column("Log Files", anchor="w")
        self.log_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.log_tree.tag_configure("highlight", background="#FFBE98")

        log_files = get_log_files(Path(LOGS_DIR))  # Update this path

        for log_file in log_files:
            self.log_tree.insert("", "end", iid=log_file, values=[log_file])

        text_frame = ttk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        self.text_widget = tk.Text(text_frame, wrap="word")
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self.log_tree.bind("<<TreeviewSelect>>", self.on_log_selection)

        # Select the first item (most recent log) if available
        first_item = self.log_tree.get_children()
        if first_item:
            self.log_tree.selection_set(first_item[0])
            self.log_tree.focus(first_item[0])
            self.log_tree.event_generate("<<TreeviewSelect>>")

    def on_log_selection(self, event):
        for item in self.log_tree.get_children():
            self.log_tree.item(item, tags=())

        selected_item = self.log_tree.selection()
        if selected_item:
            self.log_tree.item(selected_item[0], tags=("highlight",))

            log_file_path = Path(LOGS_DIR) / selected_item[0]  # Update this path
            try:
                with open(log_file_path, "r") as file:
                    content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", content)
            except Exception as e:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", f"Error reading log file: {str(e)}")

    def close_window(self, event):
        self.window.destroy()

class CalculateTotalsDialog:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Totals")
        self.create_widgets()
        self.window.bind(f"<{get_modifier_key()}-w>", self.close_window)
        self.window.bind(f"<{get_modifier_key()}-W>", self.close_window)

    def create_widgets(self):
        shifts = data_manager.get_shifts().values()
        
        number_of_shifts = len(shifts)
        total_hours_worked = sum(float(shift["Duration (hrs)"]) for shift in shifts)
        total_gross_pay = sum(float(shift["Gross pay"]) for shift in shifts)
        total_tasks_completed = sum(int(shift.get("Tasks completed", 0)) for shift in shifts)
        
        tax_liability = total_gross_pay * 0.27
        net_income = total_gross_pay - tax_liability

        columns = ("Description", "Value")
        self.totals_tree = ttk.Treeview(self.window, columns=columns, show="headings")
        self.totals_tree.heading("Description", text="Description", anchor="w")
        self.totals_tree.heading("Value", text="Value", anchor="w")
        self.totals_tree.column("Description", anchor="w", width=200)
        self.totals_tree.column("Value", anchor="e", width=150)
        self.totals_tree.pack(expand=True, fill="both")

        self.totals_tree.insert("", "end", values=("Shifts Worked", number_of_shifts))
        self.totals_tree.insert("", "end", values=("Total Hours Worked", f"{total_hours_worked:.2f}"))
        self.totals_tree.insert("", "end", values=("Total Tasks Completed", total_tasks_completed))
        self.totals_tree.insert("", "end", values=("Total Gross Pay", f"${total_gross_pay:.2f}"))
        self.totals_tree.insert("", "end", values=("Estimated Tax Liability (27%)", f"${tax_liability:.2f}"))
        self.totals_tree.insert("", "end", values=("Estimated Net Income", f"${net_income:.2f}"))

    def close_window(self, event):
        self.window.destroy()
