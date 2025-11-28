import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def perform_clustering(data, features, n_clusters=3):
    """
    Applies K-Means clustering to the dataset
    """
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    data['Cluster'] = kmeans.fit_predict(scaled_features)
    
    # Visualization
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        x=scaled_features[:, 0],
        y=scaled_features[:, 1],
        hue=data['Cluster'],
        palette='viridis'
    )
    plt.title("Clustering Analysis")
    plt.show()
    
    return data, kmeans, scaler