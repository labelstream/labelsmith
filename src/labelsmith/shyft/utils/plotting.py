import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
from mpld3 import plugins
from typing import Dict, List, Union, Tuple, Optional
from pathlib import Path
import json
import tempfile
import webbrowser
import logging
from datetime import datetime
from labelsmith.shyft.constants import APP_DATA_DIR, DATA_FILE_PATH

logger = logging.getLogger(__name__)

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
        trend = self.productivity_earnings_trend(window)
        
        if start_date:
            trend = trend[trend['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            trend = trend[trend['Date'] <= pd.to_datetime(end_date)]

        fig, ax = plt.subplots(figsize=(figsize[0]/100, figsize[1]/100))
        
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
        
        if valid_data.empty:
            logger.warning("No valid data available for plotting.")
            return ""
        
        scatter = ax.scatter(valid_data['Date'], valid_data[y_column], 
                             c=valid_data['Gross_pay'], cmap='viridis', 
                             s=50, alpha=0.8,
                             vmin=min_earnings, vmax=max_earnings)
        
        line, = ax.plot(valid_data['Date'], valid_data[rolling_column], alpha=0.5, color='red', linewidth=2)

        ax.set_title(f'{window}-Day Rolling Average: {y_label} and Earnings', fontsize=14, pad=20)
        ax.set_xlabel('Date', fontsize=12, labelpad=10)
        ax.set_ylabel(y_label, fontsize=12, labelpad=10)
        
        cbar = plt.colorbar(scatter, label='Daily Gross Pay')
        cbar.ax.tick_params(labelsize=10)
        cbar.ax.set_ylabel('Daily Gross Pay', fontsize=12, labelpad=10)
        
        cbar.set_ticks([min_earnings, (min_earnings + max_earnings) / 2, max_earnings])
        cbar.set_ticklabels([f'${min_earnings:.2f}', f'${(min_earnings + max_earnings) / 2:.2f}', f'${max_earnings:.2f}'])

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)

        max_y = valid_data[y_column].max()
        min_y = valid_data[y_column].min()
        ax.set_ylim(min_y * 0.9, max_y * 1.1)
        plt.setp(ax.get_yticklabels(), fontsize=10)

        ax.grid(True, linestyle='--', color='#E0E0E0', alpha=0.1)
        
        legend = ax.legend([line, scatter], ['Rolling Average', f'Daily {y_label}'], 
                           loc='upper left', fontsize=10, framealpha=0.95)
        legend.get_frame().set_facecolor('#F8F8F8')

        plt.tight_layout(pad=2.0)

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

        plt.close(fig)
        
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
        plotter.plot_interactive_trend(window=7, metric='tasks')

    @staticmethod
    def plot_productivity_custom():
        plotter = Plotting()
        window = int(input("Enter the number of days for the rolling average (default 7): ") or 7)
        metric = input("Enter the metric to plot (tasks/time): ").lower()
        if metric not in ['tasks', 'time']:
            print("Invalid metric. Using 'tasks' as default.")
            metric = 'tasks'
        start_date = input("Enter start date (YYYY-MM-DD) or press Enter for all data: ")
        end_date = input("Enter end date (YYYY-MM-DD) or press Enter for all data: ")
        
        plotter.plot_interactive_trend(window=window, metric=metric, start_date=start_date or None, end_date=end_date or None)