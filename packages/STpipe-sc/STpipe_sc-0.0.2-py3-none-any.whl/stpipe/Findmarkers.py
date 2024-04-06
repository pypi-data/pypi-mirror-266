import diffxpy.api as de
import numpy as np
from sklearn.utils.sparsefuncs import mean_variance_axis
from scipy.sparse import issparse


def findallmarkers(cdata, cluster_key, min_pct=0.1, only_pos=True):
    """
        Find marker genes for each cluster in cdata.

        Parameters:
            cdata (Anndata): An Anndata object.
            cluster_key (str): The key representing the cell cluster annotations in the observation metadata of the Anndata object.
            min_pct (float, optional): The minimum percentage threshold for filtering sparse genes. Defaults to 0.1.
            only_pos (bool, optional): Whether to consider only genes with positive log2 fold change. Defaults to True.

        Returns:
            cdata (Anndata): An Anndata object with marker genes identified for each cell cluster. The marker genes and related statistical information are stored in the `uns` attribute of the Anndata object under the key 'markers_all'.
        """
    clusters = cdata.obs[cluster_key].unique()
    cluster_markers = {}
    for cluster in clusters:
        cdata.obs['group'] = ['other' if x == cluster else 'current' for x in cdata.obs[cluster_key]]
        cluster_cells = cdata[cdata.obs['group'] == 'current']
        other_cells = cdata[cdata.obs['group'] == 'other']
        pct1 = np.mean(cluster_cells.X > 0, axis=0).A1 if issparse(cluster_cells.X) else np.mean(cluster_cells.X > 0, axis=0)
        pct2 = np.mean(other_cells.X > 0, axis=0).A1 if issparse(other_cells.X) else np.mean(other_cells.X > 0, axis=0)
        if issparse(cdata.X):
            mean1, _ = mean_variance_axis(axis=0, X=cluster_cells.X)
            mean2, _ = mean_variance_axis(axis=0, X=other_cells.X)
        else:
            mean1 = cluster_cells.X.mean(axis=0)
            mean2 = other_cells.X.mean(axis=0)

        selected_genes = (pct1 >= min_pct) | (pct2 >= min_pct)
        np.float = float
        test_result = de.test.t_test(
            data=cdata[:, selected_genes],
            grouping=cdata.obs["group"],
            is_logged=True
        )
        result = test_result.summary()
        result['pct1'] = pct1[selected_genes]
        result['pct2'] = pct2[selected_genes]
        if only_pos:
            result = result[result['log2fc'] > 0]

        cluster_markers[cluster] = result
    cdata.uns['markers_all'] = cluster_markers

    return cdata


def find_markers_between_groups(cdata, cluster_key, group1, group2, min_pct=0.1, only_pos=True):
    """
        Find marker genes between two specified groups in cdata.

        Parameters:
            cdata (Anndata): An Anndata object containing the single-cell data.
            cluster_key (str): The key representing the cell cluster annotations in the observation metadata of the Anndata object.
            group1 (str): The name of the first group for comparison.
            group2 (str): The name of the second group for comparison.
            min_pct (float, optional): The minimum percentage threshold for filtering sparse genes. Defaults to 0.1.
            only_pos (bool, optional): Whether to consider only genes with positive log2 fold change. Defaults to True.

        Returns:
            cdata(Anndata): An Anndata object with marker genes identified between the specified groups. The marker genes and related statistical information are stored in the `uns` attribute of the Anndata object under a key formatted as 'DGE_group1_group2'.
        """
    tmp = cdata[(cdata.obs[cluster_key] == group1) | (cdata.obs[cluster_key] == group2)].copy()
    tmp = findallmarkers(cdata=tmp, cluster_key=cluster_key, min_pct=min_pct, only_pos=only_pos)
    key_name = f"DGE_{group1}_{group2}"
    cdata.uns[key_name] = tmp.uns['markers_all']

    return cdata