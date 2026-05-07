# workflow.py
from utils.preprocessing import load_and_preprocess_data, prepare_features
from analysis.clustering import perform_clustering
from analysis.anomaly_detection import detect_anomalies
from analysis.prediction import train_consumption_model
from analysis.insights import generate_recommendations
from utils.visualization import plot_consumption_trends
from utils.preprocessing import load_and_preprocess_data
from utils.model_interface import model_manager
from utils.visualization import ZESCOVisualizer
import pandas as pd
# workflow.py
from utils.model_interface import model_manager


    # ... rest of your existing workflow code ...
class ZESCOWorkflow:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None
    
    def run_full_analysis(self):
        """Execute complete analytics workflow"""
        self.load_and_preprocess()
        self.cluster_customers()
        self.detect_anomalies()
        self.generate_forecasts()
        return self.generate_report()
    
    def load_and_preprocess(self):
        """Load and prepare data"""
        self.data = load_and_preprocess_data(self.data_path)
        return self
    
    def cluster_customers(self):
        """Perform customer segmentation"""
        features = self.data[['Energy_Consumption_kWh', 'Payment_Status', 'Usage_Type']]
        self.data['Cluster'] = model_manager.segment_customers(features)
        return self
    
    def detect_anomalies(self, sensitivity='medium'):
        """Identify anomalous consumption patterns"""
        features = self.data[['Energy_Consumption_kWh']]
        self.data['Anomaly'] = model_manager.detect_anomalies(features, sensitivity)
        return self
    
    def generate_forecasts(self, horizon=30):
        """Create consumption forecasts"""
        features = self.data[['Region', 'Usage_Type', 'Payment_Status']]
        self.forecast = model_manager.forecast_consumption(features, horizon)
        return self
    
    
    def generate_report(self):
        """Compile all analysis results"""
        return {
            'raw_data': self.data,
            'forecast': self.forecast,
            'visualizations': {
                'geospatial': ZESCOVisualizer.plot_geospatial(self.data),
                'clusters': ZESCOVisualizer.plot_clusters(self.data),
                'anomalies': ZESCOVisualizer.plot_anomalies(self.data)
            },
            'metrics': {
                'total_customers': len(self.data),
                'anomaly_rate': self.data['Anomaly'].mean(),
                'avg_consumption': self.data['Energy_Consumption_kWh'].mean()
            }
        }
def run_analysis(file_path):
    # 1. Load and preprocess
    data = load_and_preprocess_data(file_path)
    features, scaler = prepare_features(data)
    
    # 2. Clustering
    data, kmeans, _ = perform_clustering(data, features)
    data = generate_recommendations(data)
    
    # 3. Anomaly detection
    data, iso_forest = detect_anomalies(data, features)
    
    # 4. Prediction
    model, mse = train_consumption_model(
        data, 
        data[['Region', 'Usage_Type', 'Payment_Status']],
        data['Energy_Consumption_kWh']
    )
    
    return {
        'data': data,
        'models': {
            'kmeans': kmeans,
            'iso_forest': iso_forest,
            'regressor': model
        },
        'metrics': {
            'mse': mse
        }
    }