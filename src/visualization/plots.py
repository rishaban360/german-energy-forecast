import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
from pathlib import Path

class EnergyPlots:
  """Class containing all visualization methods for energy data analysis."""
  
  def __init__(self):
      # Set style for all plots
      plt.style.use('dark_background')
      self.default_figsize = (12, 6)
      self.colors = {
          'actual': '#2ecc71',    # green
          'forecast': '#3498db',   # blue
          'error': '#e74c3c',     # red
          'baseline': '#95a5a6'    # gray
      }

  def save_plot(self, fig: plt.Figure, filename: str, save_dir: str = 'reports/figures/'):
      """Save plot to specified directory."""
      Path(save_dir).mkdir(parents=True, exist_ok=True)
      fig.savefig(Path(save_dir) / f"{filename}.png", dpi=300, bbox_inches='tight')
      plt.close(fig)

  def plot_time_series(self, 
                      actual: pd.Series, 
                      forecast: pd.Series,
                      title: str = 'Energy Load Time Series',
                      save: bool = False,
                      filename: str = 'time_series') -> plt.Figure:
      """Plot time series of actual and forecasted loads."""
      fig, ax = plt.subplots(figsize=self.default_figsize)
      
      ax.plot(actual.index, actual, 
              label='Actual Load', 
              color=self.colors['actual'])
      ax.plot(forecast.index, forecast, 
              label='Forecast Load', 
              color=self.colors['forecast'])
      
      ax.set_title(title)
      ax.set_xlabel('Time')
      ax.set_ylabel('Load [MW]')
      ax.legend()
      ax.grid(True, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_distribution(self,
                        actual: pd.Series,
                        forecast: pd.Series,
                        save: bool = False,
                        filename: str = 'distribution') -> plt.Figure:
      """Plot distribution of actual and forecasted loads."""
      fig, ax = plt.subplots(figsize=self.default_figsize)
      
      sns.kdeplot(data=actual, label='Actual Load', 
                  color=self.colors['actual'], ax=ax)
      sns.kdeplot(data=forecast, label='Forecast Load', 
                  color=self.colors['forecast'], ax=ax)
      
      ax.set_title('Load Distribution')
      ax.set_xlabel('Load [MW]')
      ax.set_ylabel('Density')
      ax.legend()
      ax.grid(True, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_scatter_comparison(self,
                            actual: pd.Series,
                            forecast: pd.Series,
                            save: bool = False,
                            filename: str = 'scatter') -> plt.Figure:
      """Create scatter plot of actual vs forecast values."""
      # Align the data on common timestamps
      common_idx = actual.index.intersection(forecast.index)
      actual_aligned = actual[common_idx]
      forecast_aligned = forecast[common_idx]
      
      fig, ax = plt.subplots(figsize=self.default_figsize)
      
      ax.scatter(actual_aligned, forecast_aligned, alpha=0.5, 
                color=self.colors['actual'], label='Load Points')
      
      # Perfect prediction line
      min_val = min(actual_aligned.min(), forecast_aligned.min())
      max_val = max(actual_aligned.max(), forecast_aligned.max())
      ax.plot([min_val, max_val], [min_val, max_val], 
              '--', color=self.colors['baseline'], 
              label='Perfect Forecast')
      
      ax.set_title('Actual vs Forecast Load')
      ax.set_xlabel('Actual Load [MW]')
      ax.set_ylabel('Forecast Load [MW]')
      ax.legend()
      ax.grid(True, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_error_analysis(self,
                          actual: pd.Series,
                          forecast: pd.Series,
                          save: bool = False,
                          filename: str = 'error_analysis') -> plt.Figure:
      """Plot error analysis including error distribution and time series."""
      errors = forecast - actual
      
      fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
      
      # Error time series
      ax1.plot(errors.index, errors, color=self.colors['error'])
      ax1.axhline(y=0, color=self.colors['baseline'], linestyle='--')
      ax1.set_title('Forecast Error Over Time')
      ax1.set_xlabel('Time')
      ax1.set_ylabel('Error [MW]')
      ax1.grid(True, alpha=0.2)
      
      # Error distribution
      sns.histplot(errors, ax=ax2, color=self.colors['error'])
      ax2.axvline(x=0, color=self.colors['baseline'], linestyle='--')
      ax2.set_title('Error Distribution')
      ax2.set_xlabel('Error [MW]')
      ax2.set_ylabel('Count')
      ax2.grid(True, alpha=0.2)
      
      plt.tight_layout()
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_daily_pattern(self,
                        actual: pd.Series,
                        forecast: pd.Series,
                        save: bool = False,
                        filename: str = 'daily_pattern') -> plt.Figure:
      """Plot average daily pattern."""
      actual_hourly = actual.groupby(actual.index.hour).mean()
      forecast_hourly = forecast.groupby(forecast.index.hour).mean()
      
      fig, ax = plt.subplots(figsize=self.default_figsize)
      
      ax.plot(actual_hourly.index, actual_hourly, 
              label='Actual Load', color=self.colors['actual'])
      ax.plot(forecast_hourly.index, forecast_hourly, 
              label='Forecast Load', color=self.colors['forecast'])
      
      ax.set_title('Average Daily Load Pattern')
      ax.set_xlabel('Hour of Day')
      ax.set_ylabel('Average Load [MW]')
      ax.legend()
      ax.grid(True, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_weekly_pattern(self,
                       actual: pd.Series,
                       forecast: pd.Series,
                       save: bool = False,
                       filename: str = 'weekly_pattern') -> plt.Figure:
    """Plot weekly pattern analysis."""
    # Align the data first
    common_idx = actual.index.intersection(forecast.index)
    actual = actual[common_idx]
    forecast = forecast[common_idx]
    
    # Calculate daily averages
    actual_daily = actual.groupby(actual.index.dayofweek).mean()
    forecast_daily = forecast.groupby(forecast.index.dayofweek).mean()
    errors_daily = abs(forecast - actual).groupby(actual.index.dayofweek).mean()
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Full week days list
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # 1. Average Load by Day
    ax1.plot(days, [actual_daily.get(i, np.nan) for i in range(7)], 
            'o-', label='Actual Load', color=self.colors['actual'])
    ax1.plot(days, [forecast_daily.get(i, np.nan) for i in range(7)], 
            'o-', label='Forecast Load', color=self.colors['forecast'])
    
    ax1.set_title('Average Daily Load Pattern')
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Average Load [MW]')
    ax1.legend()
    ax1.grid(True, alpha=0.2)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 2. Average Daily Error
    ax2.bar(days, [errors_daily.get(i, np.nan) for i in range(7)],
            color=self.colors['error'], alpha=0.7)
    ax2.set_title('Average Daily Forecast Error')
    ax2.set_xlabel('Day of Week')
    ax2.set_ylabel('Mean Absolute Error [MW]')
    ax2.grid(True, alpha=0.2)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # Add data coverage note
    available_days = sorted(actual_daily.index)
    coverage_text = (
        f'Data Coverage: {len(available_days)}/7 days\n'
        f'Available: {", ".join(days[i] for i in available_days)}\n'
        f'Period: {actual.index.min().strftime("%Y-%m-%d")} to '
        f'{actual.index.max().strftime("%Y-%m-%d")}'
    )
    
    fig.text(0.02, 0.02, coverage_text,
             fontsize=10,
             bbox=dict(facecolor='black', alpha=0.1),
             ha='left')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for coverage text
    
    if save:
        self.save_plot(fig, filename)
    
    return fig

  def plot_error_heatmap(self,
                        actual: pd.Series,
                        forecast: pd.Series,
                        save: bool = False,
                        filename: str = 'error_heatmap') -> plt.Figure:
      """Create heatmap of average absolute errors by hour and day of week."""
      # Align the data first
      common_idx = actual.index.intersection(forecast.index)
      actual = actual[common_idx]
      forecast = forecast[common_idx]
      
      errors = abs(forecast - actual)
      
      # Initialize the error matrix with zeros
      error_matrix = np.zeros((24, 7))
      counts_matrix = np.zeros((24, 7))
      
      # Fill the matrices
      for idx, error in errors.items():
          hour = idx.hour
          day = idx.dayofweek
          error_matrix[hour, day] += error
          counts_matrix[hour, day] += 1
      
      # Calculate averages, avoiding division by zero
      with np.errstate(divide='ignore', invalid='ignore'):
          error_matrix = np.divide(error_matrix, counts_matrix)
          error_matrix = np.nan_to_num(error_matrix, 0)  # Replace NaN with 0
      
      # Create the plot
      fig, ax = plt.subplots(figsize=(12, 8))
      
      days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      
      im = ax.imshow(error_matrix, cmap='RdYlBu_r', aspect='auto')
      
      # Customize the plot
      plt.colorbar(im, label='Average Absolute Error [MW]')
      
      ax.set_title('Forecast Error Heatmap by Hour and Day')
      ax.set_xlabel('Day of Week')
      ax.set_ylabel('Hour of Day')
      
      # Set ticks
      ax.set_xticks(range(len(days)))
      ax.set_xticklabels(days, rotation=45)
      ax.set_yticks(range(24))
      ax.set_yticklabels(range(24))
      
      # Add grid
      ax.set_xticks(np.arange(-.5, 7, 1), minor=True)
      ax.set_yticks(np.arange(-.5, 24, 1), minor=True)
      ax.grid(which='minor', color='w', linestyle='-', linewidth=0.5, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def plot_rolling_metrics(self,
                          actual: pd.Series,
                          forecast: pd.Series,
                          window: int = 24,
                          save: bool = False,
                          filename: str = 'rolling_metrics') -> plt.Figure:
      """Plot rolling mean absolute error and bias."""
      errors = forecast - actual
      abs_errors = abs(errors)
      
      # Calculate rolling metrics
      rolling_mae = abs_errors.rolling(window=window).mean()
      rolling_bias = errors.rolling(window=window).mean()
      
      fig, ax = plt.subplots(figsize=self.default_figsize)
      
      ax.plot(rolling_mae.index, rolling_mae, 
              label='Rolling MAE', color=self.colors['error'])
      ax.plot(rolling_bias.index, rolling_bias, 
              label='Rolling Bias', color=self.colors['forecast'],
              linestyle='--')
      
      ax.set_title(f'{window}h Rolling Forecast Metrics')
      ax.set_xlabel('Time')
      ax.set_ylabel('Error [MW]')
      ax.legend()
      ax.grid(True, alpha=0.2)
      
      if save:
          self.save_plot(fig, filename)
      
      return fig

  def create_analysis_report(self,
                            actual: pd.Series,
                            forecast: pd.Series,
                            save_dir: str = 'reports/figures/') -> None:
      """Generate and save all plots for analysis."""
      self.plot_time_series(actual, forecast, save=True, 
                          filename='time_series')
      self.plot_distribution(actual, forecast, save=True, 
                            filename='distribution')
      self.plot_scatter_comparison(actual, forecast, save=True, 
                                  filename='scatter')
      self.plot_error_analysis(actual, forecast, save=True, 
                              filename='error_analysis')
      self.plot_daily_pattern(actual, forecast, save=True, 
                            filename='daily_pattern')
      #self.plot_weekly_pattern(actual, forecast, save=True, 
      #                      filename='weekly_pattern')
      self.plot_error_heatmap(actual, forecast, save=True, 
                            filename='error_heatmap')
      self.plot_rolling_metrics(actual, forecast, save=True, 
                            filename='rolling_metrics')

