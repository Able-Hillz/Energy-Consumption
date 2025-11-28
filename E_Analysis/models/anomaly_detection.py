import joblib
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, contamination=0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)
    
    def train(self, data):
        self.model.fit(data)
        return self
    
    def predict(self, data, sensitivity='medium'):
        sensitivity_map = {'low': 0.01, 'medium': 0.05, 'high': 0.1}
        self.model.set_params(contamination=sensitivity_map.get(sensitivity, 0.05))
        return self.model.predict(data)
    
    @classmethod
    def load(cls, path):
        return joblib.load(path)
    
    def save(self, path):
        joblib.dump(self, path)