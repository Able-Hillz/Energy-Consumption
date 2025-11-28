# utils/preprocessing.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_and_preprocess_data(file_path="data/energy_data.csv"):
    """Load and preprocess data with datetime handling"""
    try:
        data = pd.read_csv(file_path)
        # Convert timestamp if exists
        if 'Timestamp' in data.columns:
            data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
            data = data.dropna(subset=['Timestamp'])
        return data, None
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame(), None
    
    # Create appliance columns if they don't exist
    appliances = ['AC', 'Heating', 'Lighting', 'Electronics']
    for app in appliances:
        if f'{app}_Consumption' not in data.columns:
            data[f'{app}_Consumption'] = data['Energy_Consumption_kWh'] * 0.25  # Even distribution
    
    return data, encoders

def prepare_features(data):
    """Prepare features for modeling with fallbacks"""
    base_features = ['Energy_Consumption_kWh', 'Region', 'Usage_Type']
    available_features = [col for col in base_features if col in data.columns]
    
    if not available_features:
        raise ValueError("No valid features found in dataset")
    
    features = data[available_features]
    scaler = StandardScaler()
    
    if len(features.columns) > 0:
        scaled_features = scaler.fit_transform(features)
        return scaled_features, scaler
    return None, None

def add_meter_numbers(data):
    """Ensure meter numbers exist in dataset"""
    if 'Meter_Number' not in data.columns:
        # Generate synthetic meter numbers if they don't exist
        data['Meter_Number'] = ['METER' + str(10000 + i) for i in range(len(data))]
    return data