import tkinter as tk
from tkinter import ttk, messagebox
from labelsmith.shyft.core.data_manager import data_manager
from labelsmith.shyft.utils.time_utils import validate_time_format, calculate_duration, format_to_two_decimals
from labelsmith.shyft.utils.system_utils import get_modifier_key
from labelsmith.shyft.gui.custom_widgets import IndependentAskString

class ManualEntryForm:
    def __init__(self, parent, callback):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Manual Entry")
        self.callback = callback
        self.create_widgets()
        self.window.bind(f"<{get_modifier_key()}-w>", self.close_window)
        self.window.bind(f"<{get_modifier_key()}-W>", self.close_window)
        self.window.bind("<Return>", self.submit)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_widgets(self):
        self.entries = {}
        fields = [
            "Date", "Model ID", "Project ID", "In (hh:mm)",
            "Out (hh:mm)", "Hourly rate", "Tasks completed"
        ]
        uppercase_fields = ["Model ID", "Project ID"]

        for field in fields:
            row = ttk.Frame(self.window)
            label = ttk.Label(row, width=20, text=field, anchor="w")
            entry_var = tk.StringVar()
            entry = ttk.Entry(row, textvariable=entry_var)
            if field in uppercase_fields:
                entry_var.trace_add(
                    "write", lambda *_, var=entry_var: var.set(var.get().upper())
                )
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries[field] = entry

        if "Tasks completed" in self.entries:
            self.entries["Tasks completed"].insert(0, "0")

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Cancel", command=self.close_window).pack(side=tk.LEFT, padx=5)
        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit)
        self.submit_button.pack(side=tk.RIGHT, padx=5)

    def submit(self, event=None):
        try:
            new_data = {field: entry.get() for field, entry in self.entries.items()}
            self.validate_entries(new_data)
            duration_hrs = calculate_duration(new_data["In (hh:mm)"], new_data["Out (hh:mm)"])
            new_data["Duration (hrs)"] = format_to_two_decimals(duration_hrs)
            hourly_rate = float(new_data["Hourly rate"])
            gross_pay = hourly_rate * duration_hrs
            new_data["Gross pay"] = format_to_two_decimals(gross_pay)
            new_data["Tasks completed"] = str(int(new_data["Tasks completed"]))

            new_id = data_manager.get_max_shift_id() + 1
            formatted_id = f"{new_id:04d}"
            data_manager.add_shift(formatted_id, new_data)
            self.close_window()
            self.callback()
            messagebox.showinfo("Success", f"Shift logged successfully. {new_data['Tasks completed']} tasks completed.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def validate_entries(self, data):
        if any(v == "" for v in data.values()):
            raise ValueError("All fields must be filled out.")
        validate_time_format(data["In (hh:mm)"])
        validate_time_format(data["Out (hh:mm)"])
        try:
            float(data["Hourly rate"])
            int(data["Tasks completed"])
        except ValueError:
            raise ValueError("Invalid input for 'Hourly rate' or 'Tasks completed'. Please enter numerical values.")

    def close_window(self, event=None):
        self.window.destroy()
        self.parent.focus_force()

class EditShiftForm:
    def __init__(self, parent, shift_id, callback):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Shift")
        self.shift_id = shift_id
        self.callback = callback
        self.shift_data = data_manager.get_shifts()[self.shift_id]
        self.create_widgets()
        self.window.bind(f"<{get_modifier_key()}-w>", self.close_window)
        self.window.bind(f"<{get_modifier_key()}-W>", self.close_window)
        self.window.bind("<Return>", self.submit)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_widgets(self):
        self.entries = {}
        self.entry_vars = {}
        fields = [
            "Date", "Model ID", "Project ID", "In (hh:mm)", "Out (hh:mm)",
            "Duration (hrs)", "Hourly rate", "Gross pay", "Tasks completed"
        ]
        uppercase_fields = ["Model ID", "Project ID"]

        for field in fields:
            row = ttk.Frame(self.window)
            label = ttk.Label(row, width=15, text=field, anchor="w")
            entry_var = tk.StringVar(value=str(self.shift_data.get(field, "")))
            self.entry_vars[field] = entry_var
            entry = ttk.Entry(row, textvariable=entry_var)
            
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries[field] = entry

        for field in uppercase_fields:
            entry_var = self.entry_vars[field]
            entry_var.trace_add(
                "write", lambda *_, var=entry_var: var.set(var.get().upper())
            )

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Cancel", command=self.close_window).pack(side=tk.LEFT, padx=5)
        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit)
        self.submit_button.pack(side=tk.RIGHT, padx=5)

    def submit(self, event=None):
        try:
            updated_data = {field: var.get() for field, var in self.entry_vars.items()}
            self.validate_entries(updated_data)
            data_manager.update_shift(self.shift_id, updated_data)
            self.close_window()
            self.callback()
            messagebox.showinfo("Success", "Shift updated successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def validate_entries(self, data):
        if any(v == "" for v in data.values()):
            raise ValueError("All fields must be filled out.")
        validate_time_format(data["In (hh:mm)"])
        validate_time_format(data["Out (hh:mm)"])
        try:
            float(data["Hourly rate"])
            float(data["Gross pay"])
            int(data["Tasks completed"])
        except ValueError:
            raise ValueError("Invalid input for numerical fields. Please enter valid numbers.")

    def close_window(self, event=None):
        self.window.destroy()
        self.parent.focus_force()

