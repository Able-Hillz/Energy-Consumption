# models/clustering.py
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

class CustomerSegmenter:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.features = ['Energy_Consumption_kWh', 'Payment_Status']
    
    def fit(self, data):
        """Train the clustering model"""
        if isinstance(data, pd.DataFrame):
            features = data[self.features]
        else:
            features = data
            
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        self.model.fit(scaled_features)
        return self
    
    def predict(self, data):
        """Assign clusters to data"""
        if isinstance(data, pd.DataFrame):
            features = data[self.features]
        else:
            features = data
            
        scaled_features = self.scaler.transform(features)
        return self.model.predict(scaled_features)
    
    def fit_predict(self, data):
        """Train and predict clusters in one step"""
        self.fit(data)
        return self.predict(data)
    
    def get_cluster_centers(self):
        """Get the cluster centers in original scale"""
        return self.scaler.inverse_transform(self.model.cluster_centers_)
    
    @classmethod
    def load(cls, path):
        """Load a saved model"""
        return joblib.load(path)
    
    def save(self, path):
        """Save the model"""
        joblib.dump(self, path)