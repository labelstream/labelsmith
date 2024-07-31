import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
from mpld3 import plugins
from mpld3 import plugins
from typing import Dict, List, Union, Tuple, Optional
from pathlib import Path
import json
import appdirs
import os
import tempfile
import webbrowser
import logging
from datetime import datetime

class ShyftMetrics:
    def __init__(self, data_file: Union[str, Path]):
        self.data_file = Path(data_file)
        self.df = self._load_data()
        self.app_name = "Labelsmith"
        self.app_author = "kosmolebryce"

    def _load_data(self) -> pd.DataFrame:
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data['data'], orient='index')
        df['Date'] = pd.to_datetime(df['Date'])
        df['Duration (hrs)'] = pd.to_numeric(df['Duration (hrs)'], errors='coerce')
        df['Hourly rate'] = pd.to_numeric(df['Hourly rate'], errors='coerce')
        df['Gross pay'] = pd.to_numeric(df['Gross pay'], errors='coerce')
        df['Tasks completed'] = pd.to_numeric(df['Tasks completed'], errors='coerce').fillna(0).astype(int)
        
        df['Avg time per task (min)'] = df.apply(self._calculate_avg_time_per_task, axis=1)
        
        return df.sort_values('Date')

    def _calculate_avg_time_per_task(self, row: pd.Series) -> float:
        if row['Tasks completed'] > 0 and row['Duration (hrs)'] > 0:
            return (row['Duration (hrs)'] * 60) / row['Tasks completed']
        else:
            return float('nan')

    def get_data_dir(self) -> Path:
        data_dir = Path(appdirs.user_data_dir(self.app_name, self.app_author))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def productivity_earnings_trend(self, window: int = 7) -> pd.DataFrame:
        trend = self.df.groupby('Date').agg({
            'Tasks completed': 'sum',
            'Avg time per task (min)': 'mean',
            'Gross pay': 'sum'
        }).reset_index()
        trend = trend.sort_values('Date')
        trend['Rolling Tasks'] = trend['Tasks completed'].rolling(window=window, min_periods=1).mean()
        trend['Rolling Avg Time'] = trend['Avg time per task (min)'].rolling(window=window, min_periods=1).mean()
        trend['Rolling Earnings'] = trend['Gross pay'].rolling(window=window, min_periods=1).mean()
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
        
        min_earnings = trend['Gross pay'].min()
        max_earnings = trend['Gross pay'].max()
        
        if metric == 'tasks':
            y_column = 'Tasks completed'
            rolling_column = 'Rolling Tasks'
            y_label = 'Tasks Completed'
            tooltip_label = 'Daily Tasks'
        elif metric == 'time':
            y_column = 'Avg time per task (min)'
            rolling_column = 'Rolling Avg Time'
            y_label = 'Average Time per Task (minutes)'
            tooltip_label = 'Avg Time per Task'
        else:
            raise ValueError("Invalid metric. Choose 'tasks' or 'time'.")

        valid_data = trend.dropna(subset=[y_column, rolling_column, 'Gross pay'])
        
        scatter = ax.scatter(valid_data['Date'], valid_data[y_column], 
                             c=valid_data['Gross pay'], cmap='viridis', 
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
                    for d, t, r, e in zip(valid_data['Date'], valid_data[y_column], valid_data[rolling_column], valid_data['Gross pay'])],
            voffset=10,
            hoffset=10
        )
        plugins.connect(fig, tooltip)

        if not save_path:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                save_path = tmp.name

        if isinstance(save_path, str):
            save_path = self.get_data_dir() / save_path

        html = mpld3.fig_to_html(fig)
        html = html.replace('<div id="', f'<div style="width: {figsize[0]}px; height: {figsize[1]}px;" id="')
        
        with open(save_path, 'w') as f:
            f.write(html)
        
        logging.info(f"Interactive plot saved to: {save_path}")
        
        if auto_open:
            webbrowser.open('file://' + os.path.realpath(save_path))

        plt.close(fig)
        
        return str(save_path)

    def calculate_efficiency_metrics(self) -> Dict[str, float]:
        daily_metrics = self.df.groupby('Date').agg({
            'Tasks completed': 'sum',
            'Avg time per task (min)': 'mean',
            'Duration (hrs)': 'sum',
            'Gross pay': 'sum'
        })
        
        return {
            'Avg Tasks per Hour': (daily_metrics['Tasks completed'] / daily_metrics['Duration (hrs)']).mean(),
            'Avg Time per Task (min)': daily_metrics['Avg time per task (min)'].mean(),
            'Avg Earnings per Hour': (daily_metrics['Gross pay'] / daily_metrics['Duration (hrs)']).mean(),
            'Best Day (Tasks)': daily_metrics['Tasks completed'].max(),
            'Best Day (Efficiency)': daily_metrics['Avg time per task (min)'].min(),
            'Best Day (Earnings)': daily_metrics['Gross pay'].max()
        }

    def generate_report(self) -> Dict[str, Union[float, int]]:
        efficiency_metrics = self.calculate_efficiency_metrics()
        return {
            'Total Hours Worked': self.df['Duration (hrs)'].sum(),
            'Total Tasks Completed': self.df['Tasks completed'].sum(),
            'Total Gross Pay': self.df['Gross pay'].sum(),
            'Average Hourly Rate': self.df['Hourly rate'].mean(),
            'Overall Avg Tasks Per Hour': self.df['Tasks completed'].sum() / self.df['Duration (hrs)'].sum(),
            'Overall Avg Time per Task (min)': self.df['Avg time per task (min)'].mean(),
            'Overall Earnings Per Task': self.df['Gross pay'].sum() / self.df['Tasks completed'].sum(),
            'Average Daily Tasks per Hour': efficiency_metrics['Avg Tasks per Hour'],
            'Average Daily Time per Task (min)': efficiency_metrics['Avg Time per Task (min)'],
            'Average Daily Earnings per Hour': efficiency_metrics['Avg Earnings per Hour'],
            'Best Day (Tasks)': efficiency_metrics['Best Day (Tasks)'],
            'Best Day (Efficiency)': efficiency_metrics['Best Day (Efficiency)'],
            'Best Day (Earnings)': efficiency_metrics['Best Day (Earnings)']
        }