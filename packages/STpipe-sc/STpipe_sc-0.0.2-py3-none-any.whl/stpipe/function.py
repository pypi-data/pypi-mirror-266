import numpy as np
from scipy.sparse import csr_matrix, issparse
import dask
import dask.array as da
from numba import njit, prange
from skmisc.loess import loess
import sklearn
import pandas as pd
from pca import pca
from openTSNE import TSNE
from sklearn.neighbors import NearestNeighbors
import igraph as ig
import sinfonia
import tangram as tg
from skimage import io
import os
import anndata
from shapely.geometry import MultiPoint


def insert_tiff(adata, image_dir='./'):
    """
        Insert TIFF images into Anndata object.

        This function reads TIFF images from the specified directory and inserts them into the Anndata object.

        Parameters:
            adata (anndata.AnnData): Anndata object.
            image_dir (str, optional): Directory path containing the TIFF images. Default is './'.

        Returns:
            adata (anndata.AnnData): Anndata object with TIFF images inserted into the 'spatial' attribute under the 'uns' category.
        """
    image_dir = image_dir
    image_data = {}

    for filename in os.listdir(image_dir):
        if filename.endswith(('.tif', '.tiff')):
            tiff_image_path = os.path.join(image_dir, filename)

            tiff_image = io.imread(tiff_image_path)
            tiff_image = np.repeat(tiff_image[..., np.newaxis], 3, axis=2)
            library_id = os.path.splitext(filename)[0]

            image_data[library_id] = {"images": {"hires": tiff_image},
                                      "scalefactors": {"tissue_hires_scalef": 1, "spot_diameter_fullres": 1}}
    adata.uns['spatial'] = image_data
    return adata


@njit(parallel=True, cache=True)
def _var_nb_col(a, ddof=0):
    n = len(a)
    m = a.sum(axis=0) / (n - ddof)
    v = np.zeros(a.shape[1])
    for j in prange(a.shape[1]):
        for i in range(n):
            v[j] += abs(a[i, j] - m[j]) ** 2
    return v / (n - ddof)

@njit(parallel=True, cache=True)
def _norm(X, mean, Y):
    num_rows, num_cols = X.shape
    norm_values = np.empty_like(X)
    for i in prange(num_rows):
        for j in prange(num_cols):
            norm_values[i, j] = (X[i, j] - mean[j]) / np.sqrt(10 ** Y[j])
    return norm_values

def filter_cells(adata, min_genes):
    """
        Retain cells that express a minimum number of genes.

        Parameters:
            adata (AnnData): An anndata object.
            min_genes (int): The minimum number of genes a cell expresses.

        Returns:
            adata (anndata.AnnData): A filtered anndata object.
        """
    adata=adata.copy()
    adata.obs['n_genes'] = (adata.X > 0).sum(axis=1)
    selected_cells = adata.obs['n_genes'] >= min_genes
    adata = adata[selected_cells, :].copy()
    return adata

def filter_genes(adata, min_cells):
    """
        Retain genes that are expressed in at least a specified number of cells.

        Parameters:
            adata (AnnData): An anndata object.
            min_cells (int): The minimum number of cells in which a gene is expressed.

        Returns:
            adata (anndata.AnnData): A filtered anndata object.
        """
    if issparse(adata.X):
        n_cells = adata.X.getnnz(axis=0)
    else:
        n_cells = np.count_nonzero(adata.X, axis=0)
    adata.var['n_cells']=n_cells
    n_cells = adata.var['n_cells']
    selected_genes = np.where(n_cells >= min_cells)[0]
    adata = adata[:, selected_genes].copy()
    return adata

def _process_csr_matrix(matrix, scale_factor):
    if isinstance(matrix, np.ndarray):
        matrix = matrix * (scale_factor / matrix.sum(axis=1)[:, np.newaxis])
        matrix = np.log1p(matrix)
    else:
        matrix = csr_matrix(matrix.multiply(scale_factor / matrix.sum(axis=1)))
        matrix = matrix.log1p()
    return matrix


def _split_csr_matrix(matrix, n):
    rows = matrix.shape[0]
    row_indices = [i * rows // n for i in range(n)] + [rows]
    return [matrix[row_indices[i]:row_indices[i+1]] for i in range(n)]

def lognormal(adata, scale_factor=10000, num_chunks=30):
    """
        Apply log-normalization to the 'X' attribute.

        Parameters:
            adata (AnnData): An anndata object.
            scale_factor (float): Scale factor for cell-level normalization (default:10000).
            num_chunks (int): Number of data chunks for parallel processing (default: 30).

        Returns:
            adata (anndata.AnnData): A new anndata object with log-normalized data in the 'X' attribute.
        """
    chunks = _split_csr_matrix(adata.X, num_chunks)
    results = [da.from_delayed(dask.delayed(_process_csr_matrix)(chunk, scale_factor=scale_factor), shape=chunk.shape, dtype=chunk.dtype) for chunk in chunks]

    adata.X = csr_matrix(da.vstack(results).compute())
    return adata

def vst_highly_variable_genes(adata, n_top_genes=2000, span=0.3):
    """
        Identify highly variable genes using the VST (Variance Stabilizing Transformation) method.

        Parameters:
            adata (AnnData): An anndata object.
            n_top_genes (int): Number of highly variable genes to select (default: 2000).
            span (float): Span parameter for the LOESS regression (default: 0.3).

        Returns:
            adata (anndata.AnnData): A new anndata object with added information about highly variable genes in the 'var' attribute.
        """
    if issparse(adata.X):
        mean,var=sklearn.utils.sparsefuncs.mean_variance_axis(adata.X,axis=0)
        estimat_var = np.zeros((adata.X.shape[1]))
        y = np.log10(var)
        x = np.log10(mean)
        not_const = var > 0
        v = loess(x[not_const], y[not_const], span=span)
        v.fit()
        estimat_var[not_const] = v.outputs.fitted_values
        std = np.sqrt(10 ** estimat_var)
        vmax = np.sqrt(adata.X.shape[0])
        clip_val = std * vmax + mean
        mask = adata.X.data > clip_val[adata.X.indices]
        adata.X.data[mask] = clip_val[adata.X.indices[mask]]
        norm_var = (1 / ((adata.X.shape[0] - 1) * np.square(std))) * ((
            adata.X.shape[0] * np.square(mean)) + np.array(adata.X.power(2).sum(axis=0))
            - 2 * np.array(adata.X.sum(axis=0)) * mean)
        norm_var = np.squeeze(norm_var)
    else:
        var = _var_nb_col(adata.X)
        mean = adata.X.mean(0)
        estimat_var = np.zeros((adata.X.shape[1]))
        y = np.log10(var)
        x = np.log10(mean)
        not_const = var > 0
        v = loess(x[not_const], y[not_const], span=span)
        v.fit()
        estimat_var[not_const] = v.outputs.fitted_values
        norm_values = _norm(adata.X, mean, estimat_var)
        norm_values = np.where(norm_values > np.sqrt(adata.shape[0]), np.sqrt(adata.shape[0]), norm_values)
        norm_var = _var_nb_col(norm_values)

    df = pd.DataFrame(index=np.array(adata.var_names))
    df["variances_norm"] = norm_var
    df["means"] = mean
    df.sort_values("variances_norm", ascending=False, inplace=True)
    df["highly_variable"] = False
    df.iloc[:n_top_genes, df.columns.get_loc("highly_variable")] = True
    df = df.loc[adata.var_names]
    adata = adata.copy()
    adata.var["highly_variable"] = df["highly_variable"].values
    adata.var["variances_norm"] = df["variances_norm"]
    adata.var['means'] = df['means']
    return adata


def svg(adata, n_top_genes=2000, mode='moran_geary', n_neighbors=30):
    """
        Perform spatially variable gene analysis (SVG) on Anndata object.

        Parameters:
            adata (anndata.AnnData): Anndata object containing spatial gene expression data.
            n_top_genes (int, optional): Number of top genes to select as spatially variable genes. Default is 2000.
            mode (str, optional): Mode for SVG analysis. Options are 'moran_geary', 'moran' or 'geary'. Default is 'moran_geary'.
            n_neighbors (int, optional): Number of nearest neighbors used to construct the spatial neighbor graph. Default is 30.

        Returns:
            adata (anndata.AnnData): Anndata object with spatially variable genes identified and stored in the 'var' attribute.
        """
    adata = sinfonia.spatially_variable_genes(adata, n_top_genes=n_top_genes, mode=mode, n_neighbors=n_neighbors)
    return adata


def scale(adata,centering=True,max_value=10):
    """
        Scale the expression values of genes.

        Parameters:
            adata (AnnData): An anndata object.
            centering (bool): Whether to center the data (default: True).
                If True, the data is centered by subtracting the mean expression of each gene.
                If False, only scaling is performed.
            max_value (float or None): Maximum value for scaled data (default: 10).
                If provided, the scaled values are clipped to this maximum value.

        Returns:
            adata (anndata.AnnData): A new anndata object with scaled gene expression values in the 'X' attribute.
        """
    if issparse(adata.X):
        means, variances = sklearn.utils.sparsefuncs.mean_variance_axis(adata.X, axis=0)
        stds = np.sqrt(variances)
        stds[stds == 0] = 1
        if centering:
            adata.X = adata.X.toarray()
            adata.X -= means
            adata.X /= stds
            if max_value is not None:
                adata.X[adata.X > max_value] = max_value
                adata.X[adata.X < -max_value] = -max_value
            return adata
        else:
            sklearn.utils.sparsefuncs.inplace_column_scale(adata.X, 1 / stds)
            return adata
    else:
        means = np.mean(adata.X, axis=0)
        stds = np.std(adata.X, axis=0)
        stds[stds == 0] = 1
        if centering:
            adata.X -= means
        adata.X /= stds
        if max_value is not None:
            adata.X[adata.X > max_value] = max_value
            adata.X[adata.X < -max_value] = -max_value
        return adata

def PCA(adata,n_components=50,random_state=42,method='pca'):
    """
        Perform Principal Component Analysis (PCA) on  anndata.

        Parameters:
            adata (AnnData): An anndata object.
            n_components (Union[None, int, float]) :Number of PCs to be returned. When n_components is set >0, the specified number of PCs is returned. When n_components is set between [0..1], the number of PCs is returned that covers at least this percentage of variance. for example: n_components=None means return all PCs. n_components=0.95 means return the number of PCs that cover at least 95% of variance. n_components=3 means return the top 3 PCs.
            random_state (int or None): Seed for random number generation (default: 42).
            method (str): The method used for PCA. 'pca' means Principal Component Analysis. 'sparse_pca' means Sparse Principal Components Analysis. 'trunc_svd' means truncated SVD (aka LSA).

        Returns:
            adata (anndata.AnnData): A new anndata object with PCA results stored in the 'obsm' and 'varm' attributes.
        """
    print("[pca] >A Python Package for Principal Component Analysis (https://github.com/erdogant/pca)")
    row_labels = adata.obs_names
    col_labels = adata.var_names
    model = pca(n_components=n_components, random_state=random_state, method=method, detect_outliers=None)
    results = model.fit_transform(adata.X, row_labels=row_labels, col_labels=col_labels)
    adata.obsm['X_pca'] = results['PC']
    adata.obsm['X_pca'] = adata.obsm['X_pca'].values
    adata.varm['PCs'] = results['loadings'].T
    adata.uns['pca'] = {}
    adata.uns['pca']['variance_ratio'] = results['variance_ratio']
    adata.uns['pca']['explained_var'] = results['explained_var']
    print('[pca] >done.')
    return adata

def tsne(adata, input=15, perplexity=30, learning_rate='auto', random_seed=42,early_exaggeration=12, metric='euclidean',n_jobs=1,**kwargs):
    """
        Perform t-distributed Stochastic Neighbor Embedding (t-SNE) dimensionality reduction on single-cell RNA-seq data.

        Parameters:
            adata (AnnData): An anndata object.
            input (int or str, optional): (default: 15).
                If an integer, it specifies the number of principal components from PCA to use as input for t-SNE.
                If a string, it can be the name of an existing 'obsm' field in the AnnData object to use as input.
                If the string does not correspond to an existing field, the function falls back to using the adata.X.

            perplexity (float, optional): Perplexity parameter for t-SNE (default: 30).
                Perplexity can be thought of as the continuous :math:`k` number of nearest neighbors,
                for which t-SNE will attempt to preserve distances.

            learning_rate (str, float): Learning rate for t-SNE optimization (default: 'auto').
                The learning rate for t-SNE optimization. When ``learning_rate="auto"``
                the appropriate learning rate is selected according to max(200, N / 12),
                as determined in Belkina et al. "Automated optimized parameters for
                T-distributed stochastic neighbor embedding improve visualization and
                analysis of large datasets", 2019.

            random_seed (int, RandomState): Seed for random number generation (default: 42).
                If the value is an int, random_state is the seed used by the random
                number generator. If the value is a RandomState instance, then it will
                be used as the random number generator. If the value is None, the random
                number generator is the RandomState instance used by `np.random`.

            early_exaggeration (float): Early exaggeration parameter for t-SNE (default: 12).
                Early exaggeration increases attractive forces between data points in the initial embedding.

            metric (str): Distance metric for t-SNE (default: 'euclidean').
                The distance metric used to measure pairwise distances between data points.

            n_jobs (int): The number of threads to use while running t-SNE. This follows the scikit-learn convention,
                ``-1`` meaning all processors, ``-2`` meaning all but one, etc.

            **kwargs (typing.Any): Additional parameters for openTSNE

        Returns:
            adata (anndata.AnnData): A new anndata object with t-SNE results stored in the 'obsm' attribute as 'X_tsne'.
        """
    if isinstance(input, int):
        if isinstance(adata.obsm['X_pca'], pd.DataFrame):
            X = adata.obsm['X_pca'].values[:, :input]
        else:
            X = adata.obsm['X_pca'][:, :input]

    elif isinstance(input, str):
        if input in adata.obsm:
            X = adata.obsm[input]
        else:
            X = adata.X
    tsne = TSNE(
        perplexity=perplexity,
        learning_rate=learning_rate,
        random_state=random_seed,
        early_exaggeration=early_exaggeration,
        metric=metric,
        n_jobs=n_jobs,
        **kwargs
    )
    embedding = tsne.fit(X)
    adata.obsm['X_tsne'] = np.array(embedding)
    return adata


def find_neighbors(adata, n_components=30, n_neighbors=10, metric='euclidean', n_jobs=1):
    """
        Find nearest neighbors in PCA space.

        This function finds the nearest neighbors in the principal component analysis (PCA) space of the given Anndata object.

        Parameters:
            adata (anndata.AnnData): Anndata object containing gene expression data.
            n_components (int, optional): Number of principal components to use. Default is 30.
            n_neighbors (int, optional): Number of neighbors to find. Default is 10.
            metric (str, optional): Distance metric to use for finding neighbors. Default is 'euclidean'.
            n_jobs (int, optional): Number of parallel jobs to run for neighbor search. Default is 1.

        Returns:
            adata (anndata.AnnData): Anndata object with neighbor information stored in the 'uns' attribute under the key 'neighbors'.
                The neighbor distances are stored in 'dist' and neighbor indices are stored in 'indices'.
        """
    if isinstance(adata.obsm['X_pca'], pd.DataFrame):
        pcs = adata.obsm['X_pca'].values[:, :n_components]
    else:
        pcs = adata.obsm['X_pca'][:, :n_components]

    nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric=metric, n_jobs=n_jobs)
    nn_model.fit(pcs)
    distances, indices = nn_model.kneighbors(pcs)
    adata.uns['neighbors'] = {}
    adata.uns['neighbors']['dist'] = distances
    adata.uns['neighbors']['indices'] = indices
    return adata


def leiden(adata, resolution=1.0):
    """
        Perform Leiden clustering on Anndata object.

        This function performs Leiden community detection on the given Anndata object's neighborhood graph.

        Parameters:
            adata (anndata.AnnData): Anndata object containing gene expression data.
            resolution (float, optional): Resolution parameter for controlling the granularity of the communities. Default is 1.0.

        Returns:
            adata (anndata.AnnData): Anndata object with Leiden community labels assigned to observations stored in the 'obs' attribute under the key 'leiden'.
        """
    graph = ig.Graph(directed=False)
    graph.add_vertices(len(adata.obs))
    edges = [(i, neighbor) for i, neighbors in enumerate(adata.uns['neighbors']['indices']) for neighbor in neighbors]
    graph.add_edges(edges)
    partition = graph.community_leiden(objective_function='modularity', resolution=resolution)
    adata.obs['leiden'] = partition.membership
    adata.obs['leiden'] = pd.Categorical(adata.obs['leiden'])

    return adata


##adata,bdata both lognormalized
def falsepositive(ad_sp, ad_sc, train_gene=[], device='cuda:0', density_prior='rna_count_based', celltype=None):
    """
        Identify false-positive genes between Stereo-seq data and scRNA-seq data.

        Parameters:
            ad_sp (anndata.AnnData): Anndata object containing Stereo-seq data.
            ad_sc (anndata.AnnData): Anndata object containing scRNA-seq data.
            train_gene (list): List of genes to use for training. Default is an empty list.
            density_prior (str, ndarray or None): Spatial density of spots, when is a string, value can be 'rna_count_based' or 'uniform', when is a ndarray, shape = (number_spots,). This array should satisfy the constraints sum() == 1. If None, the density term is ignored. Default value is 'rna_count_based'.
            device (str, optional): Device to use for computation. Default is 'cuda:0'.
            celltype (str or None, optional): Cell type key in ad_sp.obs. If provided, the cell types in the scRNA-seq will be mapped to the spatial transcriptomic data. Default value is None.

        Returns:
            moran_ad_sp (pandas.Series): Pandas series containing Moran's I statistic for Stereo-seq data.\n
            moran_ad_sc (pandas.Series): Pandas series containing Moran's I statistic for scRNA-seq data.\n
            ad_ge (anndata.AnnData): AnnData object represents the scRNA-seq data mapping to the Stereo-seq space.
        """
    if 'moranI' not in ad_sp.var:
        ad_sp = sinfonia.spatially_variable_genes(ad_sp, mode='moran', coordinate_key='spatial')
    tg.pp_adatas(ad_sc, ad_sp, genes=train_gene)
    ad_map = tg.map_cells_to_space(adata_sc=ad_sc, adata_sp=ad_sp, density_prior=density_prior, device=device,
                                   verbose=False)
    if celltype is not None:
        tg.project_cell_annotations(ad_map, ad_sp, annotation=celltype)
    ad_ge = tg.project_genes(adata_map=ad_map, adata_sc=ad_sc)
    ad_ge.obsm['spatial'] = ad_sp.obsm['spatial']
    ad_ge = sinfonia.spatially_variable_genes(ad_ge, mode='moran', coordinate_key='spatial')
    moran_ad_sp=ad_sp.var['moranI']
    moran_ad_sc = ad_ge.var['moranI']
    return moran_ad_sp, moran_ad_sc, ad_ge, ad_sp


def generate_membership_anndata(dd, bb, celltype='cluster'):
    """
        Generate an Anndata object representing metacell-based gene expression.

        Parameters:
            dd (anndata.AnnData): Anndata object which .X is raw count.
            bb (anndata.AnnData): Anndata object containing spatial membership information.
            celltype (str): The key in bb.obs that represents the cell type

        Returns:
            Anndata (anndata.Anndata): An Anndata object representing metacell-based gene expression.
                The expression values are aggregated based on membership categories from the 'membership' column in bb.
                Spatial coordinates are computed as the centroids of cells belonging to each membership category.
        """
    new_data = np.zeros((len(bb.obs['membership'].unique()), dd.shape[1]))

    new_obs = {'membership': [], 'spatial': [], 'metacell_celltype': []}

    for membership_category in bb.obs['membership'].unique():
        cell_indices = np.where(bb.obs['membership'] == membership_category)[0]
        cell_counts = dd.X[cell_indices]
        gene_counts_sum = np.sum(cell_counts, axis=0)
        new_data[len(new_obs['membership'])] = gene_counts_sum

        cell_coordinates = dd.obsm['spatial'][cell_indices]
        multi_point = MultiPoint(cell_coordinates)
        centroid = multi_point.centroid
        new_obs['membership'].append(membership_category)
        new_obs['spatial'].append(centroid.coords[0])

        cluster_counts = bb.obs[celltype][cell_indices].value_counts()
        max_count = cluster_counts.max()
        most_frequent_clusters = cluster_counts[cluster_counts == max_count]
        if len(most_frequent_clusters) == 1:
            cell_type = most_frequent_clusters.index[0]
        else:
            cell_type = 'unknown'
        new_obs['metacell_celltype'].append(cell_type)

    new_anndata = anndata.AnnData(X=new_data, obsm={'spatial': np.array(new_obs['spatial'])}, var=dd.var)
    new_anndata.obs['membership'] = bb.obs['membership'].unique()
    new_anndata.obs['metacell_celltype'] = new_obs['metacell_celltype']
    return new_anndata
