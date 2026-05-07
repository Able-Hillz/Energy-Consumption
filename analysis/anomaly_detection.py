from sklearn.ensemble import IsolationForest

def detect_anomalies(data, features, contamination=0.05):
    """
    Detects anomalies using Isolation Forest
    """
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    data['Anomaly'] = iso_forest.fit_predict(features)
    data['Anomaly'] = data['Anomaly'].apply(lambda x: 1 if x == -1 else 0)
    return data, iso_forest