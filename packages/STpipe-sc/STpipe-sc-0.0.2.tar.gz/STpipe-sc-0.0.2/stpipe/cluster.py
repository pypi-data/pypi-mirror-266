import anndata2ri
from rpy2.robjects import r
import numpy as np

anndata2ri.activate()

def cluster(cdata, K_set, neighborhood_size, n_PCs):
    """
        Stereo-seq data spatial clustering.

        Parameters:
            cdata (Anndata): Anndata object containing the single-cell data.
            K_set (list): List of integers specifying the range of cluster numbers to consider.for example:np.arange(10,30)
            neighborhood_size (int): Size of the neighborhood for computing adjacency matrix.
            n_PCs (int): Number of principal components to use.

        Returns:
            cdata (Anndata): An Anndata object with cluster labels assigned to observations.
        """
    r.assign("cdata", cdata)
    r.assign("K_set", K_set)
    r.assign("neighborhood_size", neighborhood_size)
    r.assign("n_PCs", n_PCs)
    r('''
    cdata <- as(cdata, "SingleCellExperiment")
    library(SC.MEB)
    library(SingleCellExperiment)
    pos = as.matrix(colData(cdata)[,c("row","col")])
    Adj_sp = getneighborhood_fast(pos, neighborhood_size)
    y = reducedDim(cdata, "PCA")[,1:n_PCs]
    set.seed(114)
    beta_grid = seq(0,4,0.2)
    parallel=TRUE
    num_core = 3
    PX = TRUE
    maxIter_ICM = 10
    maxIter = 50
    fit = SC.MEB(y, Adj_sp, beta_grid = beta_grid, K_set= K_set, parallel=parallel, num_core = num_core, PX = PX, maxIter_ICM=maxIter_ICM, maxIter=maxIter)
    selectKPlot(fit, K_set = K_set, criterion = "BIC")
    out = selectK(fit, K_set = K_set, criterion = "BIC")
    ''')
    out = r['out']
    best_K_label_flat = np.array(out.rx2('best_K_label')).flatten()
    cdata.obs['cluster'] = best_K_label_flat.astype(str)

    return cdata