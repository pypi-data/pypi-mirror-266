import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage

# Generate synthetic data
data, _ = make_blobs(n_samples=300, centers=4, random_state=42)

# K-Means clustering
kmeans = KMeans(n_clusters=4, random_state=42)
kmeans_labels = kmeans.fit_predict(data)

# AGNES (Agglomerative Clustering)
agg_clustering = AgglomerativeClustering(n_clusters=4)
agg_labels = agg_clustering.fit_predict(data)

# Evaluate clustering quality using silhouette score
kmeans_silhouette = silhouette_score(data, kmeans_labels)
agg_silhouette = silhouette_score(data, agg_labels)

# Plot the results
plt.figure(figsize=(12, 5))

# K-Means plot
plt.subplot(1, 2, 1)
plt.scatter(data[:, 0],
            data[:, 1],
            c=kmeans_labels,
            cmap='viridis',
            edgecolors='k')
plt.scatter(kmeans.cluster_centers_[:, 0],
            kmeans.cluster_centers_[:, 1],
            c='red',
            marker='x',
            s=200,
            linewidths=3)
plt.title(f'K-Means Clustering\nSilhouette Score: {kmeans_silhouette:.2f}')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')

# AGNES (Agglomerative Clustering) plot
plt.subplot(1, 2, 2)
plt.scatter(data[:, 0],
            data[:, 1],
            c=agg_labels,
            cmap='viridis',
            edgecolors='k')
plt.title(f'AGNES Clustering\nSilhouette Score: {agg_silhouette:.2f}')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')

# Show plots
plt.tight_layout()
plt.show()
