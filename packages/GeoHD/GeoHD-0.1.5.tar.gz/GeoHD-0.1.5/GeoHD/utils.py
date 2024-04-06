import numpy as np
import warnings
import random
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter

def extract_hotspots(density_data_path, window_size=10, threshold=0):
    """
    Extract hotspots from density data using a window analysis approach.

    Parameters:
        density_data_path (str): Path to the .npy file containing density data.
        window_size (int): Size of the window for maximum filter (default is 10).
        threshold (int): Threshold value for extreme regions (default is 0).

    Returns:
        hotspots (ndarray): Array containing coordinates of hotspots.
    """
    # Load density data from the saved .npy file
    density_data = np.load(density_data_path)

    # Step 1: Window analysis to get maximum values within each window
    max_density_surface = maximum_filter(density_data, size=window_size)

    # Step 2: Algebraic subtraction to get non-negative surface
    non_negative_surface = max_density_surface - density_data

    # Step 3: Reclassification algorithm to classify into extreme and non-extreme regions
    extreme_region = non_negative_surface == threshold

    # Step 4: Extract hotspots from extreme regions
    hotspots = np.argwhere(extreme_region)

    return hotspots

def visualize_hotspots(density_data, hotspots):
    """
    Visualize hotspots on the density data.

    Parameters:
        density_data (ndarray): Density data array.
        hotspots (ndarray): Array containing coordinates of hotspots.
    """
    plt.figure(figsize=(8, 6))
    plt.imshow(density_data, cmap='Purples', origin='lower')
    plt.colorbar(label='Density')
    plt.scatter(hotspots[:, 1], hotspots[:, 0], color='red', s=5, label='Hotspots')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Hotspot Extraction')
    plt.legend()
    plt.show()


def km_euclidean_distance(x1, x2):
    """Calculate the Euclidean distance between two points for K-Means."""
    return np.sqrt(np.sum((x1 - x2)**2))

def km_initialize_centroids(X, n_clusters, random_state=None):
    """Initialize centroids for K-Means clustering."""
    np.random.seed(random_state)
    centroids_indices = np.random.choice(X.shape[0], size=n_clusters, replace=False)
    centroids = X[centroids_indices]
    return centroids

def km_assign_clusters(X, centroids):
    """Assign clusters to points based on current centroids for K-Means."""
    clusters = []
    for x in X:
        distances = [km_euclidean_distance(x, centroid) for centroid in centroids]
        cluster = np.argmin(distances)
        clusters.append(cluster)
    return np.array(clusters)

def km_update_centroids(X, clusters, n_clusters):
    """Update centroids based on current cluster assignments for K-Means."""
    centroids = np.zeros((n_clusters, X.shape[1]))
    for cluster in range(n_clusters):
        cluster_points = X[clusters == cluster]
        if len(cluster_points) > 0:
            centroids[cluster] = np.mean(cluster_points, axis=0)
    return centroids

def km_plot_clusters(X, clusters, centroids):
    """Plot clusters and centroids for K-Means."""
    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, 0], X[:, 1], c=clusters, cmap='viridis', s=50, edgecolor='k')
    plt.scatter(centroids[:, 0], centroids[:, 1], marker='*', c='red', s=150, edgecolor='k')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Clusters and Centroids (K-Means)')
    plt.colorbar(label='Cluster')
    plt.grid(True)
    plt.show()

def km_kmeans_clustering(shp_file_path, n_clusters=3, max_iterations=100, visualize=True, random_state=None):
    """Perform K-Means clustering on point data from an SHP file."""
    # Suppress warnings for demonstration purposes
    warnings.filterwarnings("ignore")

    # Load the SHP file into a GeoDataFrame
    gdf = gpd.read_file(shp_file_path)

    # Extract features (coordinates) from the GeoDataFrame
    X = np.column_stack((gdf['geometry'].x, gdf['geometry'].y))

    # Initialize centroids
    centroids = km_initialize_centroids(X, n_clusters, random_state=random_state)

    # Perform K-Means iterations
    for _ in range(max_iterations):
        # Assign clusters to points
        clusters = km_assign_clusters(X, centroids)
        # Update centroids
        new_centroids = km_update_centroids(X, clusters, n_clusters)
        # Check for convergence
        if np.allclose(new_centroids, centroids):
            break
        centroids = new_centroids

    if visualize:
        # Visualize the clusters and centroids
        km_plot_clusters(X, clusters, centroids)

    return clusters, centroids

def db_range_query(X, point, eps):
    """Find neighboring points within a specified distance for DBSCAN."""
    neighbors = []
    for i, x in enumerate(X):
        if km_euclidean_distance(point, x) <= eps:
            neighbors.append(i)
    return neighbors

def db_expand_cluster(X, labels, point, neighbors, cluster_label, eps, min_samples):
    """Expand a cluster based on DBSCAN algorithm."""
    labels[point] = cluster_label
    i = 0
    while i < len(neighbors):
        neighbor = neighbors[i]
        if labels[neighbor] == -1:
            labels[neighbor] = cluster_label
            new_neighbors = db_range_query(X, X[neighbor], eps)
            if len(new_neighbors) >= min_samples:
                neighbors += new_neighbors
        elif labels[neighbor] == 0:
            labels[neighbor] = cluster_label
        i += 1

def db_dbscan_clustering(shp_file_path, eps=0.1, min_samples=5, visualize=True):
    """Perform DBSCAN clustering on point data from an SHP file."""
    # Load the SHP file into a GeoDataFrame
    gdf = gpd.read_file(shp_file_path)

    # Extract features (coordinates) from the GeoDataFrame
    X = np.column_stack((gdf['geometry'].x, gdf['geometry'].y))

    # Initialize labels array
    labels = np.zeros(len(X), dtype=int)  # 0 represents unvisited points
    current_label = 0

    for i, point in enumerate(X):
        if labels[i] != 0:
            continue

        neighbors = db_range_query(X, point, eps)
        if len(neighbors) < min_samples:
            labels[i] = -1  # Mark as noise
        else:
            current_label += 1
            db_expand_cluster(X, labels, i, neighbors, current_label, eps, min_samples)

    if visualize:
        db_visualize_clusters(X, labels)

    return labels

def db_visualize_clusters(X, labels):
    """Visualize clusters from DBSCAN clustering."""
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels) - 1  # Exclude noise points

    plt.figure(figsize=(8, 6))

    for cluster_label in range(1, n_clusters + 1):
        cluster_points = X[labels == cluster_label]
        plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {cluster_label}')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('DBSCAN Clustering')
    plt.legend()
    plt.grid(True)
    plt.show()








# Example usage:
if __name__ == "__main__":
    density_data_path = './output/AKDE_density_grid.npy'
    hotspots = extract_hotspots(density_data_path)
    visualize_hotspots(np.load(density_data_path), hotspots)
