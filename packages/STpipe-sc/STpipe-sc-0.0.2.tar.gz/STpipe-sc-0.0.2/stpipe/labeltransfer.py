import scanorama
from sklearn.metrics.pairwise import cosine_distances
import anndata
import numpy as np
import pandas as pd


def _label_transfer(dist, labels):
    lab = pd.get_dummies(labels).to_numpy().T
    class_prob = lab @ dist
    norm = np.linalg.norm(class_prob, 2, axis=0)
    class_prob = class_prob / norm
    class_prob = (class_prob.T - class_prob.min(1)) / class_prob.ptp(1)
    return class_prob


#adata bdata should be lognormalized,both genes are recommended to be highly variable
def labeltransfer(adata,bdata,celltype='celltype'):
    """
        Transfer cell type labels from scRNA-seq to Stereo-seq using Scanorama.

        It performs batch correction using Scanorama on the combined datasets and computes the label transfer based on cosine distances between the corrected embeddings.

        Parameters:
            adata (anndata.AnnData): AnnData object representing Stereo-seq.
            bdata (anndata.AnnData): AnnData object representing scRNA-seq.
            celltype (str): The key in the observation metadata of 'bdata' containing cell type labels. Default is 'celltype'.

        Returns:
            adata_transfer (anndata.AnnData): AnnData object with transferred cell type labels.
                The transferred labels are stored in the observation metadata under the key 'labeltransfer_celltype'.
                Additionally, the maximum confidence score are stored in the observation metadata under the keys 'max_score'.
        """
    bdata.obs[celltype] = bdata.obs[celltype].astype('category')
    adatas = [bdata, adata]
    adatas2 = scanorama.correct_scanpy(adatas, return_dimred=True)
    cdata = anndata.concat(
        adatas2,
        label="dataset",
        keys=["scRNA-seq", "Stereo-seq"],
        join="outer",
        uns_merge="first",
    )

    distances = 1 - cosine_distances(
        cdata[cdata.obs.dataset == "scRNA-seq"].obsm[
            "X_scanorama"
        ],
        cdata[cdata.obs.dataset == "Stereo-seq"].obsm[
            "X_scanorama"
        ],
    )
    class_prob = _label_transfer(distances, bdata.obs.celltype)
    df = pd.DataFrame(
        class_prob,
        columns=sorted(bdata.obs[celltype].cat.categories),
    )
    df['labeltransfer_celltype'] = df.apply(lambda x: x.idxmax(), axis=1)
    df['max_score'] = df.max(axis=1, numeric_only=True)
    df.index = adata.obs.index
    adata_transfer = adata.copy()
    adata_transfer.obs = pd.concat(
        [adata.obs, df], axis=1
    )
    return adata_transfer
