import tkinter as tk
from tkinter import ttk, messagebox
from labelsmith.shyft.core import config_manager, nltk_manager
from labelsmith.shyft.core.autologger import Autologger
from labelsmith.shyft.core.data_manager import data_manager, logger
from labelsmith.shyft.gui.menu import setup_menu
from labelsmith.shyft.gui.entry_forms import ManualEntryForm, EditShiftForm
from labelsmith.shyft.gui.dialogs import ViewLogsDialog, CalculateTotalsDialog
from labelsmith.shyft.gui.timer_window import TimerWindow
from labelsmith.shyft.utils.system_utils import prevent_sleep, allow_sleep, get_modifier_key
from labelsmith.shyft.gui.custom_widgets import DictionaryLookupText, CustomTooltip
from labelsmith.shyft.constants import CONFIG_FILE, LOGS_DIR
from pathlib import Path

class ShyftGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shyft")
        self.time_color = "#A78C7B"
        self.bg_color = "#FFBE98"
        self.btn_text_color = "#A78C7B"
        self.root.configure(bg=self.bg_color)
        self.config = config_manager.load_config()
        self.timer_topmost = self.config.getboolean("Theme", "timer_topmost", fallback=False)
        self.timer_topmost_var = tk.BooleanVar(value=self.timer_topmost)
        self.configure_styles()
        self.menu_bar = None
        self.theme_menu = None
        self.view_menu = None
        self.file_menu = None
        self.settings_menu = None
        self.setup_menu()
        self.create_widgets()
        self.refresh_view()
        self.timer_window = None
        self.root.resizable(True, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

        self.task_start_time = None
        self.caffeinate_process = None

        logger.info("ShyftGUI initialized.")

    def create_dictionary_lookup(self):
        self.dictionary_text = DictionaryLookupText(self.root)
        self.dictionary_text.pack(expand=True, fill='both')

    def configure_styles(self):
        self.style = ttk.Style(self.root)
        self.update_styles()
        self.style.theme_use(self.config.get("Theme", "selected", fallback="default"))

    def update_styles(self):
        self.style.map(
            "Treeview",
            background=[("selected", "#FFBE98")],
            foreground=[("selected", "black")],
        )
        self.style.configure(
            "highlight.Treeview", background="#FFBE98", foreground="black"
        )

    def create_widgets(self):
        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "ID",
                "Date",
                "Model ID",
                "Project ID",
                "In (hh:mm)",
                "Out (hh:mm)",
                "Duration (hrs)",
                "Tasks completed",  # Add this new column
                "Hourly rate",
                "Gross pay",
            ),
            show="headings",
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, anchor="w", width=100)
        self.tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.root, style="TFrame")
        button_frame.pack(side="bottom", fill="both", expand=True)

        ttk.Button(
            button_frame,
            text="Manual Entry",
            command=self.manual_entry,
            style="TButton",
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame, text="Edit Shift", command=self.edit_shift, style="TButton"
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame,
            text="Delete Shift",
            command=self.delete_shift,
            style="TButton",
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame,
            text="Refresh View",
            command=self.refresh_view,
            style="TButton",
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame, text="View Logs", command=self.view_logs, style="TButton"
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame, text="Autologger", command=self.autologger, style="TButton"
        ).pack(side="left", expand=True)
        ttk.Button(
            button_frame, text="Totals", command=self.calculate_totals, style="TButton"
        ).pack(side="left", expand=True)
        logger.info("Widgets created.")

    def setup_menu(self):
        setup_menu(self)

    def refresh_view(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        sorted_keys = sorted(data_manager.get_shifts().keys(), key=lambda x: int(x), reverse=True)

        for id in sorted_keys:
            shift = data_manager.get_shifts()[id]
            self.tree.insert("", "end", iid=id, values=(
                id, shift.get("Date", "N/A"), shift.get("Model ID", "N/A"),
                shift.get("Project ID", "N/A"), shift.get("In (hh:mm)", "N/A"),
                shift.get("Out (hh:mm)", "N/A"), shift.get("Duration (hrs)", "N/A"),
                shift.get("Tasks completed", "N/A"), shift.get("Hourly rate", "N/A"),
                shift.get("Gross pay", "N/A")
            ))

        first_item = self.tree.get_children()
        if first_item:
            self.tree.selection_set(first_item[0])
            self.tree.focus(first_item[0])

        logger.debug("Tree view populated with updated data.")

    def manual_entry(self, event=None):
        ManualEntryForm(self.root, self.refresh_view)

    def edit_shift(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a shift to edit.")
            return
        selected_id = selected_item[0]
        EditShiftForm(self.root, selected_id, self.refresh_view)

    def delete_shift(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a shift to delete.")
            return
        selected_id = selected_item[0]
        
        def on_confirm():
            try:
                data_manager.delete_shift(selected_id)
                self.refresh_view()
                logger.info(f"Shift {selected_id} deleted.")
            except FileNotFoundError as e:
                md_file_path = Path(LOGS_DIR) / f"{selected_id}.md"
                if not md_file_path.exists():
                    logger.warning(f"Markdown file for shift {selected_id} was not found during deletion: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while deleting the shift: {str(e)}")
                logger.error(f"Failed to delete shift {selected_id}: {str(e)}")
            finally:
                self.root.after(100, self.regain_focus)

        def on_cancel():
            self.root.after(100, self.regain_focus)

        # Calculate the position for the dialog
        dialog_width = 340  # Estimated width
        dialog_height = 100  # Estimated height
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        # Create a custom dialog with pre-calculated position
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirm Delete")
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        label = ttk.Label(dialog, text="Are you sure you want to delete the selected shift?")
        label.pack(pady=10)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        yes_button = ttk.Button(button_frame, text="Yes", command=lambda: [on_confirm(), dialog.destroy()])
        yes_button.pack(side=tk.LEFT, padx=10)

        no_button = ttk.Button(button_frame, text="No", command=lambda: [on_cancel(), dialog.destroy()])
        no_button.pack(side=tk.LEFT, padx=10)

        def invoke_focused_button(event):
            focused = dialog.focus_get()
            if focused in (yes_button, no_button):
                focused.invoke()

        # Bind Enter key to invoke the focused button
        dialog.bind("<Return>", invoke_focused_button)
        
        # Set focus to the No button by default
        no_button.focus_set()

        # Use after() to ensure no_button keeps focus
        dialog.after(10, no_button.focus_set)

        self.root.wait_window(dialog)

    def regain_focus(self):
        self.root.focus_force()
        self.tree.focus_set()
        if self.tree.get_children():
            self.tree.selection_set(self.tree.get_children()[0])
            self.tree.focus(self.tree.get_children()[0])

    def view_logs(self, event=None):
        return ViewLogsDialog(self.root, self.tree, self.refresh_view)

    def calculate_totals(self, event=None):
        return CalculateTotalsDialog(self.root)

    def autologger(self, event=None):
        autologger = Autologger(
            self.root,
            self.timer_window,
            self.time_color,
            self.bg_color,
            self.btn_text_color,
            self.config,
            self.menu_bar,
            self.refresh_view,
            self.tree
            )
        return autologger.start()

    def minimize_window(self, event=None):
        self.root.iconify()

    def on_quit(self, event=None):
        if self.caffeinate_process:
            allow_sleep(self.caffeinate_process)
        self.root.quit()
        logger.info("Application quit.")

    def toggle_timer_topmost(self):
        if self.timer_window:
            current_topmost_state = self.timer_window.root.attributes("-topmost")
            new_topmost_state = not current_topmost_state
            self.timer_window.root.attributes("-topmost", new_topmost_state)
            self.config.set("Theme", "timer_topmost", str(new_topmost_state))
            config_manager.save_config(self.config)
            self.timer_topmost_var.set(new_topmost_state)
            logger.debug(f"Timer topmost state set to {new_topmost_state}.")
