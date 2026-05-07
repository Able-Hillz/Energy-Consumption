# utils/utility_analysis.py
import pandas as pd
from utils.preprocessing import load_and_preprocess_data

def get_sector_data(sector):
    """Get data for specific sector with fallbacks"""
    data, _ = load_and_preprocess_data()
    
    if 'Usage_Type' not in data.columns:
        return data  # Return all data if no sector filter available
    
    sector_mapping = {
        'Residential': 0,
        'Commercial': 1,
        'Industrial': 2
    }
    
    if sector in sector_mapping:
        return data[data['Usage_Type'] == sector_mapping[sector]]
    return data

def calculate_region_metrics(data):
    """Calculate metrics with comprehensive error handling"""
    if data.empty or 'Region' not in data.columns:
        return pd.DataFrame()
    
    metrics = data.groupby('Region').agg({
        'Energy_Consumption_kWh': ['sum', 'mean', 'max'],
        'Payment_Status': lambda x: (x == 0).mean() if 'Payment_Status' in data.columns else 0
    })
    
    metrics.columns = ['Total_Consumption', 'Avg_Consumption', 
                      'Peak_Consumption', 'Non_Payment_Rate']
    return metrics.reset_index()