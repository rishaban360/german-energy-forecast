# Standard library imports
import sys
import warnings
from pathlib import Path

# Third-party imports
import numpy as np
import pandas as pd
import holidays
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

class EnhancedFeatureExtractor24h:
    """Feature extractor for 24-hour load forecasting"""
    
    def __init__(self):
        self.windows = [24, 168, 336]  # 1 day, 1 week, 2 weeks
        self.morning_peak_hours = [7, 8, 9, 10, 11]
        self.evening_peak_hours = [16, 17, 18]
        self.base_hours = [0, 1, 2, 3, 4, 22, 23]
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from input DataFrame
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input DataFrame with datetime index and 'load' column
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with extracted features
        """
        try:
            df = df.copy()
            
            # Input validation
            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError("DataFrame index must be DatetimeIndex")
            if 'load' not in df.columns:
                raise ValueError("DataFrame must contain 'load' column")
            
            # Extract basic time features
            df = self._add_time_features(df)
            
            # Add rolling statistics
            df = self._add_rolling_stats(df)
            
            # Add peak handling features
            df = self._add_peak_features(df)
            
            # Add renewable features if available
            df = self._add_renewable_features(df)
            
            # Clean up temporary columns
            df = self._cleanup_features(df)
            
            return df
            
        except Exception as e:
            print(f"Error in feature extraction: {str(e)}")
            raise
            
    def _add_time_features(self, df):
        """Add basic time-based features"""
        df['hour'] = df.index.hour
        df['weekday'] = df.index.weekday
        
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)
        
        return df
        
    def _add_rolling_stats(self, df):
        """Add rolling statistics features"""
        for window in self.windows:
            df[f'load_{window}h_mean'] = df['load'].rolling(window=window, min_periods=1).mean()
            df[f'load_{window}h_std'] = df['load'].rolling(window=window, min_periods=1).std()
            df[f'load_{window}h_min'] = df['load'].rolling(window=window, min_periods=1).min()
            df[f'load_{window}h_max'] = df['load'].rolling(window=window, min_periods=1).max()
        
        return df
        
    def _add_peak_features(self, df):
        """Add peak-specific features"""
        df['is_morning_peak'] = df.index.hour.isin(self.morning_peak_hours)
        df['is_evening_peak'] = df.index.hour.isin(self.evening_peak_hours)
        df['is_base_load'] = df.index.hour.isin(self.base_hours)
        
        for window in [3, 6, 12]:
            # Morning peak features
            morning_mask = df['is_morning_peak']
            df[f'morning_peak_{window}h_mean'] = df[morning_mask]['load'].rolling(window, min_periods=1).mean()
            df[f'morning_peak_{window}h_max'] = df[morning_mask]['load'].rolling(window, min_periods=1).max()
            
            # Evening peak features
            evening_mask = df['is_evening_peak']
            df[f'evening_peak_{window}h_mean'] = df[evening_mask]['load'].rolling(window, min_periods=1).mean()
            df[f'evening_peak_{window}h_max'] = df[evening_mask]['load'].rolling(window, min_periods=1).max()
        
        return df
        
    def _add_renewable_features(self, df):
        """Add renewable energy features if available"""
        if 'solar_yesterday' in df.columns:
            df['solar_hour_sin'] = df['solar_yesterday'] * df['hour_sin']
            df['morning_solar_ramp'] = df['is_morning_peak'] * df['solar_yesterday']
            df['evening_solar_ramp'] = df['is_evening_peak'] * df['solar_yesterday']
            
            for window in [24, 168]:
                df[f'solar_{window}h_mean'] = df['solar_yesterday'].rolling(window, min_periods=1).mean()
        
        if all(col in df.columns for col in ['wind_offshore_yesterday', 'wind_onshore_yesterday']):
            df['total_wind'] = df['wind_offshore_yesterday'] + df['wind_onshore_yesterday']
            df['wind_hour_sin'] = df['total_wind'] * df['hour_sin']
            
            for window in [24, 168]:
                df[f'wind_{window}h_mean'] = df['total_wind'].rolling(window, min_periods=1).mean()
        
        return df
        
    def _cleanup_features(self, df):
        """Remove temporary columns"""
        columns_to_drop = ['hour', 'weekday']
        return df.drop(columns=[col for col in columns_to_drop if col in df.columns]) 