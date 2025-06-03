# backend/cluster.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def get_clusters(city, start_ts, end_ts, k):
    # Load pre-merged dataset
    df = pd.read_csv('clustered_electricity_demand.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Filter by city and date range
    sub = df[(df['city'] == city) & (df['datetime'] >= start_ts) & (df['datetime'] <= end_ts)]
    if sub.empty:
        return []
    # Select features for clustering
    X = sub[['temperature','humidity','windSpeed','demand']].dropna()
    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)
    # PCA to 2D for visualization
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X_scaled)
    # K-Means clustering
    kmeans = KMeans(n_clusters=k, random_state=0).fit(X_scaled)
    labels = kmeans.labels_
    # Prepare JSON-able output
    points = []
    for i, (x, y) in enumerate(coords):
        points.append({'x': float(x), 'y': float(y), 'cluster': int(labels[i])})
    return points