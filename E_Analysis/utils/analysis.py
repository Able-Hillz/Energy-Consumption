# analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
# utils/analysis.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_consumption(data, horizon=30):
    """
    Predict future energy usage using linear regression.
    
    Args:
        data: DataFrame with columns ['Timestamp', 'Energy_Consumption_kWh']
        horizon: Days to forecast (default=30)
        
    Returns:
        forecast_df: DataFrame with columns ['ds', 'yhat'] (dates and predictions)
    """
    # 1. Prepare data
    df = data.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    daily = df.resample('D', on='Timestamp').mean().reset_index()
    
    # 2. Create features (days since start)
    daily['days'] = (daily['Timestamp'] - daily['Timestamp'].min()).dt.days
    X = daily[['days']]  # Feature matrix
    y = daily['Energy_Consumption_kWh']  # Target
    
    # 3. Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # 4. Generate future dates
    last_date = daily['Timestamp'].max()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=horizon,
        freq='D'
    )
    
    # 5. Predict
    future_days = (future_dates - daily['Timestamp'].min()).days.values.reshape(-1, 1)
    future_usage = model.predict(future_days)
    
    # 6. Return results
    return pd.DataFrame({
        'ds': future_dates,
        'yhat': future_usage
    })

def calculate_carbon(energy_kwh, region="Default"):
    """
    Calculate CO2 emissions based on energy consumption and regional grid factor
    
    Args:
        energy_kwh: Total energy consumption in kWh
        region: Geographic region for emission factor adjustment
        
    Returns:
        CO2 emissions in kilograms
    """
    # Base emission factor (kgCO2/kWh) - Zambia average
    base_factor = 0.35  # Zambia's grid emission factor
    
    # Regional adjustments (example values)
    regional_factors = {
        "Lusaka": 0.38,
        "Copperbelt": 0.42,
        "Southern": 0.33,
        "Northern": 0.30,
        "Default": 0.35
    }
    
    factor = regional_factors.get(region, regional_factors["Default"])
    return energy_kwh * factor

def detect_anomalies(data, sensitivity='medium'):
    """
    Detect anomalous energy consumption patterns
    
    Args:
        data: DataFrame with energy consumption data
        sensitivity: Detection sensitivity ('low', 'medium', 'high')
        
    Returns:
        DataFrame with detected anomalies
    """
    # Set contamination based on sensitivity
    contamination_map = {
        'low': 0.01,
        'medium': 0.05,
        'high': 0.1
    }
    contamination = contamination_map.get(sensitivity, 0.05)
    
    # Prepare features
    features = data[['Energy_Consumption_kWh']].copy()
    if 'Hour' in data.columns:
        features['Hour'] = data['Hour']
    if 'DayOfWeek' in data.columns:
        features['DayOfWeek'] = data['DayOfWeek']
    
    # Train isolation forest
    clf = IsolationForest(contamination=contamination, random_state=42)
    anomalies = clf.fit_predict(features)
    
    # Return anomalous records
    anomalies_df = data.copy()
    anomalies_df['Anomaly_Score'] = anomalies
    anomalies_df['Is_Anomaly'] = anomalies == -1
    
    return anomalies_df[anomalies_df['Is_Anomaly']].sort_values('Energy_Consumption_kWh', ascending=False)

def get_benchmarks(data, current_user, sector='residential'):
    """
    Compare user's consumption to regional/sector benchmarks
    
    Args:
        data: DataFrame containing full dataset
        current_user: Dict with user attributes (Region, Household_Size, etc.)
        sector: User sector (residential/commercial/industrial)
        
    Returns:
        Dictionary with comparison metrics
    """
    # Filter relevant data
    sector_data = data[data['Usage_Type'].str.contains(sector, case=False)]
    region_data = sector_data[sector_data['Region'] == current_user['Region']]
    
    # Calculate benchmarks
    benchmarks = {
        'regional_avg': region_data['Energy_Consumption_kWh'].mean(),
        'sector_avg': sector_data['Energy_Consumption_kWh'].mean(),
        'similar_users': region_data[
            region_data['Household_Size'] == current_user.get('Household_Size', 4)
        ]['Energy_Consumption_kWh'].mean()
    }
    return benchmarks

def predict_consumption(data, horizon=30):
    """
    Forecast future energy consumption using time series analysis
    
    Args:
        data: DataFrame with historical consumption data
        horizon: Number of periods to forecast
        
    Returns:
        DataFrame with forecasted values
    """
    # Prepare time series data
    ts_data = data.set_index('Timestamp')['Energy_Consumption_kWh'].resample('D').mean()
    
    # Fill missing values with forward fill
    ts_data = ts_data.fillna(method='ffill')
    
    # Fit ARIMA model
    model = ARIMA(ts_data, order=(1,1,1))
    model_fit = model.fit()
    
    # Generate forecast
    forecast = model_fit.get_forecast(steps=horizon)
    
    # Create forecast DataFrame
    forecast_dates = pd.date_range(
        start=ts_data.index[-1] + pd.Timedelta(days=1),
        periods=horizon
    )
    
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted_Consumption': forecast.predicted_mean,
        'Confidence_Lower': forecast.conf_int().iloc[:, 0],
        'Confidence_Upper': forecast.conf_int().iloc[:, 1]
    })
    
    return forecast_df

class EnergyAnalyzer:
    def __init__(self, data_path):
        """
        Initialize with energy data
        Args:
            data_path: Path to CSV file containing energy data
        """
        self.df = pd.read_csv(data_path)
        self._preprocess_data()
        
    def _preprocess_data(self):
        """Clean and prepare the data for analysis"""
        # Convert timestamp and extract features
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        self.df['Month'] = self.df['Timestamp'].dt.month
        self.df['Hour'] = self.df['Timestamp'].dt.hour
        self.df['Day'] = self.df['Timestamp'].dt.day
        
        # Handle negative consumption values
        self.df['Energy_Consumption_kWh'] = self.df['Energy_Consumption_kWh'].abs()
        
    def plot_consumption_trends(self, group_column='Region', time_column='Month'):
        """
        Plot energy consumption trends by selected grouping
        Args:
            group_column: Column to group by (Region, Usage_Type, etc.)
            time_column: Time period to analyze (Month, Hour, Day)
        """
        plt.figure(figsize=(12, 6))
        sns.lineplot(
            data=self.df,
            x=time_column,
            y='Energy_Consumption_kWh',
            hue=group_column,
            estimator='mean',
            ci=None
        )
        plt.title(f'Energy Consumption Trends by {group_column}')
        plt.ylabel('Consumption (kWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def generate_report(self, current_user):
        """
        Generate comprehensive analysis report
        Args:
            current_user: Dict with user attributes
        Returns:
            Dict containing all analysis results
        """
        report = {
            'anomalies': detect_anomalies(self.df),
            'benchmarks': get_benchmarks(self.df, current_user),
            'forecast': predict_consumption(self.df),
            'trends': {
                'by_region': self.df.groupby('Region')['Energy_Consumption_kWh'].mean().to_dict(),
                'by_month': self.df.groupby('Month')['Energy_Consumption_kWh'].mean().to_dict()
            }
        }
        return report