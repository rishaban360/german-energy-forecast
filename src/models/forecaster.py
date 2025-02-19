import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

class EnergyForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def prepare_features(self, df):
        # Add time-based features
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        return df[['hour', 'day_of_week', 'month']]

    def train(self, historical_load):
        """Train the model on historical load data"""
        X = self.prepare_features(historical_load)
        y = historical_load['load']
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, input_data):
        """Generate predictions for the input data"""
        if not self.is_trained:
            raise ValueError("Model needs to be trained before making predictions")
        
        X = self.prepare_features(input_data)
        return self.model.predict(X)
