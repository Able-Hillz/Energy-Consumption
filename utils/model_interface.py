from models.anomaly_detection import AnomalyDetector
from models.forecasting import ConsumptionForecaster
from models.clustering import CustomerSegmenter
import joblib
import os

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    
    def _initialize_models(self):
        # Initialize with default models
        self.anomaly_model = AnomalyDetector()
        self.forecast_model = ConsumptionForecaster()
        self.clustering_model = CustomerSegmenter()
        
        # Try to load trained models if they exist
        self.load_models()
    
    def load_models(self):
        model_dir = "models/saved_models"
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            self.anomaly_model = AnomalyDetector.load(f"{model_dir}/anomaly_model.pkl")
        except FileNotFoundError:
            pass
            
        try:
            self.forecast_model = ConsumptionForecaster.load(f"{model_dir}/forecast_model.pkl")
        except FileNotFoundError:
            pass
    
    def detect_anomalies(self, data, sensitivity='medium'):
        return self.anomaly_model.predict(data, sensitivity)
    
    def forecast_consumption(self, data, horizon=30):
        return self.forecast_model.predict(data, horizon)
    
    def segment_customers(self, data):
        return self.clustering_model.fit_predict(data)
    
    def save_models(self):
        model_dir = "models/saved_models"
        os.makedirs(model_dir, exist_ok=True)
        
        self.anomaly_model.save(f"{model_dir}/anomaly_model.pkl")
        self.forecast_model.save(f"{model_dir}/forecast_model.pkl")

# Singleton instance
model_manager = ModelManager()