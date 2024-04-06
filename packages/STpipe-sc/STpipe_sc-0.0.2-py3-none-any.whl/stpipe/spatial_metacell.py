import numpy as np
import igraph as ig
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def spatial_bigcells(adata, method='walktrap', n_pca=30, n_neighbors=200, n_jobs=4, distance_threshold=50, p=5,
                     resolution=1,celltypes='celltype',nb_trials=1,
                     weights=None, const=1, a=50, sigma=10, b=10, node_weight=None):
    """
        Detect spatial metacell using network-based clustering algorithms.

        Parameters:
            adata (anndata.AnnData): An AnnData object representing the Stereo-seq data.
            method (str, optional): The clustering method to use. Options are 'walktrap', 'edge_betweenness', 'leiden', 'multilevel', and 'infomap'.
            n_pca (int, optional): Number of principal components to use for dimensionality reduction.
            n_neighbors (int, optional): Number of neighbors to consider for constructing the k-nearest neighbor graph.
            n_jobs (int, optional): Number of parallel jobs to run for k-nearest neighbor search.
            distance_threshold (int or None, optional): Threshold distance for filtering out distant neighbors.
            p (int, optional): For method is walktrap or edge_betweenness. The desired number of cells per metacell.
            nb_trials (int): For method is infomap.The number of attempts to partition the network (can be any integer value equal or larger than 1).
            resolution (float, optional): For method is multilevel or leiden. Default is 1.
            celltypes (str, optional): Key in the observation metadata containing cell type annotations. Default is 'celltype'.
            weights (str or None, optional): Method for assigning weights to edges in the graph. Options are 'inverse_distance', 'gaussian', 'celltype', or None. Default is None.
            const (int, optional): Constant value for inverse distance weighting.
            a (int, optional): Parameter for inverse distance weighting.
            sigma (int, optional): Standard deviation parameter for Gaussian weighting.
            b (int, optional): Weight for edges based on cell type similarity.
            node_weight (str or None, optional): Key in the observation metadata containing node weights.

        Returns:
            adata (anndata.AnnData): An updated AnnData object with metacell assignments stored in the observation metadata under the key 'membership'.
            clusters (igraph.clustering.VertexClustering): A vertex clustering object representing the detected meta cell.
        """
    if isinstance(adata.obsm['X_pca'], pd.DataFrame):
        X = adata.obsm['X_pca'].values[:, :n_pca]
    else:
        X = adata.obsm['X_pca'][:, :n_pca]

    if 'spatial' in adata.obsm.keys():
        coords = adata.obsm['spatial']
    elif 'x' in adata.obs.columns and 'y' in adata.obs.columns:
        coords = adata.obs[['x', 'y']].values
    else:
        raise ValueError("Spatial coordinates (obsm['spatial']) or 'x' and 'y' obs columns are not present in adata.")
    all_distances = np.sqrt(np.sum((coords[:, None] - coords) ** 2, axis=2))
    mask_diagonal = np.eye(all_distances.shape[0], dtype=bool)
    all_distances[mask_diagonal] = np.inf
    mask_no_neighbors = np.all(all_distances > 50, axis=1)
    X = X[~mask_no_neighbors]
    coords = coords[~mask_no_neighbors]
    adata = adata[~mask_no_neighbors].copy()
    nbrs = NearestNeighbors(n_neighbors=n_neighbors, n_jobs=n_jobs).fit(X)
    distances, indices = nbrs.kneighbors(X)
    actual_distances = np.sqrt(np.sum((coords[:, None] - coords[indices]) ** 2, axis=2))
    if distance_threshold is not None:
        mask = actual_distances > distance_threshold
        indices[mask] = -1

    G = ig.Graph(directed=False)
    G.add_vertices(X.shape[0])
    edges = [(i, j) for i in range(indices.shape[0]) for j in indices[i] if j != -1 and j != i]
    G.add_edges(edges)

    if weights == 'inverse_distance':
        weights = [a / (actual_distances[i, np.where(indices[i] == j)[0][0]] + const) for i, j in edges if
                   actual_distances[i, np.where(indices[i] == j)[0][0]] != 0]
        G.es['weight'] = weights
    elif weights == 'gaussian':
        weights = [np.exp(-actual_distances[i, np.where(indices[i] == j)[0][0]] ** 2 / (2 * sigma ** 2)) for i, j in
                   edges]
        G.es['weight'] = weights
    elif weights == 'celltype':
        cell_types = adata.obs[celltypes].values
        weights = [b if cell_types[i] == cell_types[j] else 1 for i, j in edges]
        G.es['weight'] = weights

    if node_weight is not None:
        node_weight = adata.obs[node_weight]

    n_clusters = round(adata.shape[0] / p)
    if method == 'walktrap':
        dendrogram = G.community_walktrap(weights=weights)
        clusters = dendrogram.as_clustering(n=n_clusters)
    elif method == 'edge_betweenness':
        dendrogram = G.community_edge_betweenness(weights=weights)
        clusters = dendrogram.as_clustering(n=n_clusters)
    elif method == 'leiden':
        clusters = G.community_leiden(resolution=resolution, weights=weights, node_weights=node_weight, n_iterations=20)
    elif method == 'multilevel':
        clusters = G.community_multilevel(resolution=resolution, weights=weights)
    elif method == 'infomap':
        clusters = G.community_infomap(edge_weights=weights, vertex_weights=node_weight, nb_trials=nb_trials)

    adata.obs['membership'] = clusters.membership
    adata.uns['modularity'] = clusters.modularity
    adata.uns['membership_sizes'] = clusters.sizes()

    return adata, clusters
