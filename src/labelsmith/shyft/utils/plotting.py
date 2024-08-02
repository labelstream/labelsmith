import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import mpld3
from mpld3 import plugins
from typing import Dict, List, Union, Tuple, Optional
from pathlib import Path
import json
import tempfile
import threading
import webbrowser
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import datetime
from datetime import datetime
from labelsmith.shyft.constants import APP_DATA_DIR, DATA_FILE_PATH

logger = logging.getLogger("labelsmith")

class Plotting:
    def __init__(self):
        self.data_file = DATA_FILE_PATH
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame.from_dict(data['data'], orient='index')
            
            df = df.assign(
                Date=pd.to_datetime(df['Date']),
                Duration_hrs=pd.to_numeric(df['Duration (hrs)'], errors='coerce'),
                Hourly_rate=pd.to_numeric(df['Hourly rate'], errors='coerce'),
                Gross_pay=pd.to_numeric(df['Gross pay'], errors='coerce'),
                Tasks_completed=pd.to_numeric(df['Tasks completed'], errors='coerce').fillna(0).astype(int)
            )
            
            df['Avg time per task (min)'] = df.apply(self._calculate_avg_time_per_task, axis=1)
            
            return df.sort_values('Date')
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()

    @staticmethod
    def _calculate_avg_time_per_task(row: pd.Series) -> float:
        if row['Tasks_completed'] > 0 and row['Duration_hrs'] > 0:
            return (row['Duration_hrs'] * 60) / row['Tasks_completed']
        else:
            return float('nan')

    def productivity_earnings_trend(self, window: int = 7) -> pd.DataFrame:
        trend = self.df.groupby('Date').agg({
            'Tasks_completed': 'sum',
            'Avg time per task (min)': 'mean',
            'Gross_pay': 'sum'
        }).reset_index()
        trend = trend.sort_values('Date')
        trend = trend.assign(
            Rolling_Tasks=trend['Tasks_completed'].rolling(window=window, min_periods=1).mean(),
            Rolling_Avg_Time=trend['Avg time per task (min)'].rolling(window=window, min_periods=1).mean(),
            Rolling_Earnings=trend['Gross_pay'].rolling(window=window, min_periods=1).mean()
        )
        return trend

    def plot_interactive_trend(self, 
                               save_path: Optional[Union[str, Path]] = None, 
                               window: int = 7, 
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None,
                               figsize: Tuple[int, int] = (1240, 780),
                               auto_open: bool = True,
                               metric: str = 'tasks') -> str:
        def generate_plot():
            nonlocal save_path
            trend = self.productivity_earnings_trend(window)
            
            if start_date:
                trend = trend[trend['Date'] >= pd.to_datetime(start_date)]
            if end_date:
                trend = trend[trend['Date'] <= pd.to_datetime(end_date)]

            logger.debug(f"Columns in trend DataFrame: {trend.columns.tolist()}")
            if 'Gross_pay' not in trend.columns:
                logger.error("Column 'Gross_pay' is missing from the trend DataFrame.")
                return

            fig = Figure(figsize=(figsize[0]/100, figsize[1]/100))
            ax = fig.add_subplot(111)

            min_earnings = trend['Gross_pay'].min()
            max_earnings = trend['Gross_pay'].max()
            
            if metric == 'tasks':
                y_column = 'Tasks_completed'
                rolling_column = 'Rolling_Tasks'
                y_label = 'Tasks Completed'
                tooltip_label = 'Daily Tasks'
            elif metric == 'time':
                y_column = 'Avg time per task (min)'
                rolling_column = 'Rolling_Avg_Time'
                y_label = 'Average Time per Task (minutes)'
                tooltip_label = 'Avg Time per Task'
            else:
                raise ValueError("Invalid metric. Choose 'tasks' or 'time'.")

            valid_data = trend.dropna(subset=[y_column, rolling_column, 'Gross_pay'])
            
            scatter = ax.scatter(valid_data['Date'], valid_data[y_column], 
                                c=valid_data['Gross_pay'], cmap='viridis', 
                                s=50, alpha=0.8,
                                vmin=min_earnings, vmax=max_earnings)
            
            line, = ax.plot(valid_data['Date'], valid_data[rolling_column], alpha=0.5, color='red', linewidth=2)

            ax.set_title(f'{window}-Day Rolling Average: {y_label} and Earnings', fontsize=14, pad=20)
            ax.set_xlabel('Date', fontsize=12, labelpad=10)
            ax.set_ylabel(y_label, fontsize=12, labelpad=10)
            
            cbar = fig.colorbar(scatter, ax=ax, label='Daily Gross Pay')
            cbar.ax.tick_params(labelsize=10)
            cbar.ax.set_ylabel('Daily Gross Pay', fontsize=12, labelpad=10)
            
            cbar.set_ticks([min_earnings, (min_earnings + max_earnings) / 2, max_earnings])
            cbar.set_ticklabels([f'${min_earnings:.2f}', f'${(min_earnings + max_earnings) / 2:.2f}', f'${max_earnings:.2f}'])

            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.tick_params(axis='x', rotation=45, labelsize=10)

            # Correct way to set horizontal alignment
            for label in ax.get_xticklabels():
                label.set_ha('right')

            max_y = valid_data[y_column].max()
            min_y = valid_data[y_column].min()
            ax.set_ylim(min_y * 0.9, max_y * 1.1)
            ax.tick_params(axis='y', labelsize=10)

            ax.grid(True, linestyle='--', color='#E0E0E0', alpha=0.1)
            
            legend = ax.legend([line, scatter], ['Rolling Average', f'Daily {y_label}'], 
                            loc='upper left', fontsize=10, framealpha=0.95)
            legend.get_frame().set_facecolor('#F8F8F8')

            fig.tight_layout(pad=2.0)

            tooltip = plugins.PointHTMLTooltip(
                scatter,
                labels=[f"Date: {d:%Y-%m-%d}<br>{tooltip_label}: {t:.1f}<br>Rolling Avg: {r:.1f}<br>Earnings: ${e:.2f}" 
                        for d, t, r, e in zip(valid_data['Date'], valid_data[y_column], valid_data[rolling_column], valid_data['Gross_pay'])],
                voffset=10,
                hoffset=10
            )
            plugins.connect(fig, tooltip)

            if not save_path:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                    save_path = tmp.name

            if isinstance(save_path, str):
                save_path = APP_DATA_DIR / save_path

            html = mpld3.fig_to_html(fig)
            html = html.replace('<div id="', f'<div style="width: {figsize[0]}px; height: {figsize[1]}px;" id="')
            
            with open(save_path, 'w') as f:
                f.write(html)
            
            logger.info(f"Interactive plot saved to: {save_path}")
            
            if auto_open:
                webbrowser.open('file://' + str(save_path.resolve()))

        plot_thread = threading.Thread(target=generate_plot)
        plot_thread.start()
        plot_thread.join()  # Wait for the plotting to finish
        
        return str(save_path)

    def calculate_efficiency_metrics(self) -> Dict[str, float]:
        daily_metrics = self.df.groupby('Date').agg({
            'Tasks_completed': 'sum',
            'Avg time per task (min)': 'mean',
            'Duration_hrs': 'sum',
            'Gross_pay': 'sum'
        })
        
        return {
            'Avg Tasks per Hour': (daily_metrics['Tasks_completed'] / daily_metrics['Duration_hrs']).mean(),
            'Avg Time per Task (min)': daily_metrics['Avg time per task (min)'].mean(),
            'Avg Earnings per Hour': (daily_metrics['Gross_pay'] / daily_metrics['Duration_hrs']).mean(),
            'Best Day (Tasks)': daily_metrics['Tasks_completed'].max(),
            'Best Day (Efficiency)': daily_metrics['Avg time per task (min)'].min(),
            'Best Day (Earnings)': daily_metrics['Gross_pay'].max()
        }

    def generate_report(self) -> Dict[str, Union[float, int]]:
        efficiency_metrics = self.calculate_efficiency_metrics()
        return {
            'Total Hours Worked': self.df['Duration_hrs'].sum(),
            'Total Tasks Completed': self.df['Tasks_completed'].sum(),
            'Total Gross Pay': self.df['Gross_pay'].sum(),
            'Average Hourly Rate': self.df['Hourly_rate'].mean(),
            'Overall Avg Tasks Per Hour': self.df['Tasks_completed'].sum() / self.df['Duration_hrs'].sum(),
            'Overall Avg Time per Task (min)': self.df['Avg time per task (min)'].mean(),
            'Overall Earnings Per Task': self.df['Gross_pay'].sum() / self.df['Tasks_completed'].sum(),
            'Average Daily Tasks per Hour': efficiency_metrics['Avg Tasks per Hour'],
            'Average Daily Time per Task (min)': efficiency_metrics['Avg Time per Task (min)'],
            'Average Daily Earnings per Hour': efficiency_metrics['Avg Earnings per Hour'],
            'Best Day (Tasks)': efficiency_metrics['Best Day (Tasks)'],
            'Best Day (Efficiency)': efficiency_metrics['Best Day (Efficiency)'],
            'Best Day (Earnings)': efficiency_metrics['Best Day (Earnings)']
        }

    @staticmethod
    def plot_productivity_default():
        plotter = Plotting()
        plotter.plot_interactive_trend(window=7, metric='time')

    # class ProductivityPlotDialog(tk.Toplevel):
    #     def __init__(self, parent):
    #         super().__init__(parent)
    #         self.title("Productivity Plot Parameters")
    #         self.result = None
    #         self.create_widgets()
    #         self.geometry("500x300")  # Increased height to accommodate calendars
    #         self.resizable(True, True)

    #     def create_widgets(self):
    #         self.columnconfigure(0, weight=1)
    #         self.rowconfigure(0, weight=1)

    #         main_frame = ttk.Frame(self, padding="20 20 20 20")
    #         main_frame.grid(row=0, column=0, sticky="nsew")
    #         main_frame.columnconfigure(1, weight=1)

    #         # Window size input
    #         ttk.Label(main_frame, text="Rolling average window (days):").grid(row=0, column=0, sticky="w", pady=10)
    #         self.window_var = tk.IntVar(value=7)
    #         ttk.Spinbox(main_frame, from_=1, to=365, textvariable=self.window_var, width=5).grid(row=0, column=1, sticky="ew", pady=10, padx=(10,0))

    #         # Metric selection
    #         ttk.Label(main_frame, text="Metric to plot:").grid(row=1, column=0, sticky="w", pady=10)
    #         self.metric_var = tk.StringVar(value="tasks")
    #         metric_frame = ttk.Frame(main_frame)
    #         metric_frame.grid(row=1, column=1, sticky="ew", pady=10, padx=(10,0))
    #         ttk.Radiobutton(metric_frame, text="Tasks", variable=self.metric_var, value="tasks").pack(side="left", padx=(0,10))
    #         ttk.Radiobutton(metric_frame, text="Time", variable=self.metric_var, value="time").pack(side="left")

    #         # Date range selection
    #         ttk.Label(main_frame, text="Start date:").grid(row=2, column=0, sticky="w", pady=10)
    #         self.start_date_var = tk.StringVar()
    #         ttk.Entry(main_frame, textvariable=self.start_date_var, width=12).grid(row=2, column=1, sticky="ew", pady=10, padx=(10,0))
    #         ttk.Button(main_frame, text="Select", command=lambda: self.show_calendar(self.start_date_var)).grid(row=2, column=2, padx=(5,0))

    #         ttk.Label(main_frame, text="End date:").grid(row=3, column=0, sticky="w", pady=10)
    #         self.end_date_var = tk.StringVar()
    #         ttk.Entry(main_frame, textvariable=self.end_date_var, width=12).grid(row=3, column=1, sticky="ew", pady=10, padx=(10,0))
    #         ttk.Button(main_frame, text="Select", command=lambda: self.show_calendar(self.end_date_var)).grid(row=3, column=2, padx=(5,0))

    #         # Buttons
    #         button_frame = ttk.Frame(main_frame)
    #         button_frame.grid(row=4, column=0, columnspan=3, pady=(20,0), sticky="ew")
    #         button_frame.columnconfigure(0, weight=1)
    #         button_frame.columnconfigure(1, weight=1)
            
    #         ttk.Button(button_frame, text="OK", command=self.on_ok).grid(row=0, column=0, padx=(0,5), sticky="e")
    #         ttk.Button(button_frame, text="Cancel", command=self.on_cancel).grid(row=0, column=1, padx=(5,0), sticky="w")

    #     def show_calendar(self, date_var):
    #         top = tk.Toplevel(self)
    #         top.title("Select Date")
    #         top.grab_set()

    #         def on_date_select(event):
    #             date_var.set(cal.get_date())
    #             top.destroy()
            
    #         cal = Calendar(top, selectmode='day', date_pattern='y-mm-dd')
    #         cal.pack(padx=10, pady=10)
    #         cal.bind("<<CalendarSelected>>", on_date_select)
            
    #         ok_button = ttk.Button(top, text="OK", command=lambda: self.set_date(top, cal, date_var))
    #         ok_button.pack(pady=10)

    #         # Set focus to the calendar
    #         cal.focus_set()

    #     def set_date(self, top, cal, date_var):
    #         date_var.set(cal.get_date())
    #         top.destroy()

    #     def on_ok(self):
    #         try:
    #             start_date = datetime.datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
    #             end_date = datetime.datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
    #             self.result = {
    #                 'window': self.window_var.get(),
    #                 'metric': self.metric_var.get(),
    #                 'start_date': start_date.strftime('%Y-%m-%d'),
    #                 'end_date': end_date.strftime('%Y-%m-%d')
    #             }
    #             self.destroy()
    #         except ValueError:
    #             messagebox.showerror("Invalid Date", "Please enter valid dates in the format YYYY-MM-DD")

    #     def on_cancel(self):
    #         self.result = None
    #         self.destroy()

    # @classmethod
    # def plot_productivity_custom(cls):
    #     root = tk.Tk()
    #     root.withdraw()  # Hide the root window
    #     dialog = cls.ProductivityPlotDialog(root)
    #     dialog.grab_set()
    #     root.wait_window(dialog)
        
    #     if dialog.result:
    #         plotter = cls()
    #         plotter.plot_interactive_trend(
    #             window=dialog.result['window'],
    #             metric=dialog.result['metric'],
    #             start_date=dialog.result['start_date'],
    #             end_date=dialog.result['end_date']
    #         )
    #     root.destroy()