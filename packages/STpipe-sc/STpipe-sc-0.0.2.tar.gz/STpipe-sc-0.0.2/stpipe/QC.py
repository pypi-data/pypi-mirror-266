import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from stpipe import function

def markers_detected_by_diff_ngenes_scatter(adata, markers, image_width=6, image_height=6, xlabel='n_genes',
                                            ylabel='Markers detection rate',title=None,o=None, **kwargs):
    """
        Create a scatter plot to visualize the relationship between the number of genes (n_genes) and the detection rate of markers.

        Parameters:
            adata (AnnData):An AnnData object.
            markers (list): A list of marker gene names.
            image_width (int, optional): Width of the generated image. Default is 6.
            image_height (int, optional): Height of the generated image. Default is 6.
            xlabel (str, optional): Label for the X-axis. Default is 'n_genes'.
            ylabel (str, optional): Label for the Y-axis. Default is 'Markers detection rate'.
            title (str, optional): Title of the plot. If not provided, no title is displayed.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the plt.scatter function.
        """
    adata.obs['n_genes'] = (adata.X > 0).sum(axis=1)
    p = []
    for i in range(len(adata)):
        genes = adata.var_names[adata.X[i].nonzero()[1]]
        intersect = set(genes).intersection(set(markers))
        p.append(len(intersect) / len(set(markers)))

    adata.obs["Markers detection rate"] = p
    plt.figure(figsize=(image_width, image_height))
    plt.scatter(adata.obs['n_genes'], adata.obs['Markers detection rate'], **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if o is not None and isinstance(o, str):
        plt.savefig(o)

    plt.show()

def markers_detected_by_diff_ngenes_bar(adata, markers, bin=50, image_width=12, image_height=6, xlabel='n_genes',
                                        ylabel='Markers detection rate', title=None, o=None, **kwargs):
    """
        Create a bar plot to visualize the relationship between the number of genes (n_genes) and the detection rate of markers.

        Parameters:
            adata (AnnData): An AnnData object.
            markers (list): A list of marker gene names.
            bin (int, optional): The bin size for grouping n_genes values. Default is 50.
            image_width (int, optional): Width of the generated image. Default is 12.
            image_height (int, optional): Height of the generated image. Default is 6.
            xlabel (str, optional): Label for the X-axis. Default is 'n_genes'.
            ylabel (str, optional): Label for the Y-axis. Default is 'Markers detection rate'.
            title (str, optional): Title of the plot. If not provided, no title is displayed.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the plt.bar function.
        """
    adata.obs['n_genes'] = (adata.X > 0).sum(axis=1)
    bins = np.arange(0, np.ceil(adata.obs['n_genes'].max() / bin) * bin, bin).astype(int)
    adata.obs['n_genes_subset'] = np.digitize(adata.obs['n_genes'], bins)

    counts = []
    for i in range(len(adata)):
        genes = adata.var_names[adata.X[i].nonzero()[1]]
        intersect = set(genes).intersection(set(markers))
        counts.append(len(intersect))

    adata.obs["Markers intersect counts"] = counts

    subset_counts = []
    for i in range(len(bins) - 1):
        subset = adata[adata.obs['n_genes_subset'] == i + 1]
        n = 0
        for cell in subset.obs_names:
            n += subset.obs.loc[cell, 'Markers intersect counts']
        if len(subset.obs_names) > 0:
            n = n / len(subset.obs_names)
            p = n / len(set(markers))
            subset_counts.append(p)
        else:
            subset_counts.append(0)

    plt.figure(figsize=(image_width, image_height))
    plt.bar([f"{bins[i]}-{bins[i+1]}" for i in range(len(bins) - 1)], subset_counts, color='#898989',**kwargs)
    plt.xticks(rotation=90)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)

    if o is not None and isinstance(o, str):
        plt.savefig(o)

    plt.show()

def detect_markers_by_filter_cells(adata, markers, min_genes_list=list(range(0, 1400, 50)), min_cells_list=[3],
                                   image_width=5, image_height=5, xlabel='min_genes', ylabel='Percentage',
                                   title='Percentage of markers remaining',o=None, **kwargs):
    """
        Create a line plot that shows how many of the marker genes are still present in the adata after filtering,
        as you change the min_genes and the min_cells used for filtering.(The proportion of marker genes in markers)

        Parameters:
            adata (AnnData): An AnnData object.
            markers (list): A list of marker gene names.
            min_genes_list (list, optional): A list of min_genes to consider. Default list(range(0, 1400, 50)).
            min_cells_list (list, optional): A list of min_cells for gene filtering. Default [3].
            image_width (int, optional): Width of the generated image. Default is 5.
            image_height (int, optional): Height of the generated image. Default is 5.
            xlabel (str, optional): Label for the X-axis. Default is 'min_genes'.
            ylabel (str, optional): Label for the Y-axis. Default is 'Percentage'.
            title (str, optional): Title of the plot. Default is 'Percentage of markers remaining'.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the plt.plot function.
        """
    marker_overlap = {frac: [] for frac in min_cells_list}
    for frac in min_cells_list:
        for min_genes in min_genes_list:
            adata_filtered = adata.copy()
            adata_filtered = function.filter_cells(adata_filtered, min_genes=min_genes)
            adata_filtered = function.filter_genes(adata_filtered, min_cells=frac)
            remaining_genes = adata_filtered.var_names.tolist()
            overlap_genes = set(remaining_genes).intersection(set(markers))
            marker_overlap_percent = len(overlap_genes) / len(set(markers))
            marker_overlap[frac].append(marker_overlap_percent)

    plt.figure(figsize=(image_width, image_height))
    for frac in min_cells_list:
        plt.plot(min_genes_list, marker_overlap[frac], label=f'min_cells={frac}', **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.05, 0.5), loc='center left')
    if o is not None and isinstance(o, str):
        plt.savefig(o)
    plt.show()

def detect_markers_by_filter_cells2(adata, markers, min_genes_list=list(range(0, 1400, 50)), min_cells_list=[3],
                                   image_width=5, image_height=5, xlabel='min_genes', ylabel='Percentage',
                                   title='Percentage of markers detected',o=None, **kwargs):
    """
        Create a line plot that shows how many of the marker genes are still present in the adata after filtering,
        as you change the min_genes and the min_cells used for filtering.(The proportion of marker genes in adata)

        Parameters:
            adata (AnnData): An AnnData object.
            markers (list): A list of marker gene names.
            min_genes_list (list, optional): List of minimum gene counts for filtering. Default list(range(0, 1400, 50)).
            min_cells_list (list, optional): List of minimum cell counts for filtering. Default is [3].
            image_width (int, optional): Width of the generated image. Default is 5.
            image_height (int, optional): Height of the generated image. Default is 5.
            xlabel (str, optional): Label for the X-axis. Default is 'min_genes'.
            ylabel (str, optional): Label for the Y-axis. Default is 'Percentage'.
            title (str, optional): Title of the plot. Default is 'Percentage of markers detected'.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the plt.plot function.
        """
    ...
    gene_overlap = {frac: [] for frac in min_cells_list}
    for frac in min_cells_list:
        for min_genes in min_genes_list:
            adata_filtered = adata.copy()
            adata_filtered = function.filter_cells(adata_filtered, min_genes=min_genes)
            adata_filtered = function.filter_genes(adata_filtered, min_cells=frac)
            remaining_genes = adata_filtered.var_names.tolist()
            overlap_genes = set(remaining_genes).intersection(set(markers))
            overlap_percent = len(overlap_genes) / len(remaining_genes)
            gene_overlap[frac].append(overlap_percent)

    plt.figure(figsize=(image_width, image_height))
    for frac in min_cells_list:
        plt.plot(min_genes_list, gene_overlap[frac], label=f'min_cells={frac}', **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.05, 0.5), loc='center left')
    if o is not None and isinstance(o, str):
        plt.savefig(o)
    plt.show()

def cell_numbers_by_min_genes(adata, min_genes_list=list(range(0, 1400, 50)),
                                   image_width=5, image_height=5, xlabel='min_genes', ylabel='cell number',
                                   title=None,o=None, **kwargs):
    """
        Create a line plot reflecting the number of cells remaining after filtering with different min_genes

        Parameters:
            adata (AnnData): An AnnData object.
            min_genes_list (list, optional): List of minimum gene counts used for filtering cells. Default list(range(0, 1400, 50)).
            image_width (int, optional): Width of the generated plot image. Default is 5.
            image_height (int, optional): Height of the generated plot image. Default is 5.
            xlabel (str, optional): Label for the X-axis of the plot. Default is 'min_genes'.
            ylabel (str, optional): Label for the Y-axis of the plot. Default is 'cell number'.
            title (str, optional): Title of the plot. If not provided, no title will be displayed.
            o (str, optional): Path and filename for saving the plot image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the plt.plot function.
        """
    num_cells = []
    for min_gene in min_genes_list:
        adata_filtered = adata.copy()
        adata_filtered = function.filter_cells(adata_filtered, min_genes=min_gene)
        num_cells.append(adata_filtered.shape[0])

    plt.figure(figsize=(image_width, image_height))
    plt.plot(min_genes_list, num_cells, **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if o is not None and isinstance(o, str):
        plt.savefig(o)
    plt.show()

def valid_cells_per_slice(adata, min_genes_list=list(range(0, 800, 100)), image_width=5, image_height=5, xlabel='min_genes',
                          slice='id', library='current object', median_n_genes=[],ylabel='Percentage',title='Percentage of markers detected',
                          o=None, **kwargs):
    """
        Create line plots to illustrate the relationship between the library median n_genes and the percentage of valid cells per slice.

        Parameters:
            adata (AnnData): An AnnData object.
            min_genes_list (list, optional): A list of minimum gene counts for cell filtering. Default is a list from 0 to 800 with a step of 100.
            image_width (int, optional): Width of the generated image. Default is 5.
            image_height (int, optional): Height of the generated image. Default is 5.
            xlabel (str, optional): Label for the X-axis. Default is 'min_genes'.
            slice (str): Column in the observation data used for grouping slices and analyzing the percentage of valid cells.
            library (str): Source of data for calculating the median number of genes per slice. Default is 'current object', using the observation data of the current object. Alternatively, provide a list 'median_n_genes' as reference.
            median_n_genes (list, optional): If 'library' is not 'current object', provide a list of Library median gene counts as reference.
            ylabel (str, optional): Label for the Y-axis. Default is 'Percentage'.
            title (str, optional): Title of the plot. Default is 'Percentage of markers detected'.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
            **kwargs (typing.Any): Additional keyword arguments to be passed to the sns.regplot function.
        """
    adata.obs['n_genes'] = (adata.X > 0).sum(axis=1)
    if library == 'current object':
        library_median_n_genes = adata.obs.groupby(slice)['n_genes'].median().tolist()
    elif median_n_genes is not None:
        if not isinstance(median_n_genes, list):
            raise ValueError("'median_n_genes' must be a list.")
        library_median_n_genes = median_n_genes
    else:
        raise ValueError("If 'library' is not 'current object', 'median_n_genes' must be provided as a list.")

    plt.figure(figsize=(image_width, image_height))
    #colors = ['red', 'blue', 'green', 'orange', 'purple', 'gray', 'cyan', 'magenta']
    s1 = adata.obs.groupby(slice).size()
    s2_list = []
    for i, min_genes in enumerate(min_genes_list):
        adata_filtered = adata.copy()
        adata_filtered = function.filter_cells(adata_filtered, min_genes=min_genes)
        s2 = adata_filtered.obs.groupby(slice).size()
        s2_list.append(s2)
        p = s2 / s1
        index_mapping = list(range(len(s1.index)))
        sns.regplot(x=[library_median_n_genes[index_mapping[j]] for j in range(len(index_mapping))], y=p,
                    scatter_kws={'s': 2},label=f'min_genes={min_genes}', **kwargs)
        #sns.regplot(x=[library_median_n_genes[index_mapping[j]] for j in range(len(index_mapping))], y=p,scatter_kws={'s': 2}, label=f'min_genes={min_genes}', color=colors[i])

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(fontsize=6)
    plt.title(title)
    if o is not None and isinstance(o, str):
        plt.savefig(o)
    plt.show()

def additional_seq_vs_seq(adata1, adata2, min_genes_list=list(range(0, 800, 100)), image_width=5, image_height=5, xlabel='min_genes',
                          slice='id', min_cells=3, ylabel='valid cells P.',title='sequencing vs additional sequencing',slice_id=None,
                          color='blue', s=15, o=None):
    """
        Create a scatter plot to compare the percentage of valid cells in sequencing data and additional sequencing data.

        Parameters:
            adata1 (AnnData): An AnnData object representing the sequencing data.
            adata2 (AnnData): An AnnData object representing the additional sequencing data.
            min_genes_list (list, optional): A list of minimum gene counts for cell filtering. Default is a list from 0 to 800 with a step of 100.
            image_width (int, optional): Width of the generated image. Default is 5.
            image_height (int, optional): Height of the generated image. Default is 5.
            xlabel (str, optional): Label for the X-axis. Default is 'min_genes'.
            slice (str): Column in the observation data used for grouping slices.
            min_cells (int): min_cells to filter genes.
            ylabel (str, optional): Label for the Y-axis. Default is 'valid cells P.'.
            title (str, optional): Title of the plot. Default is 'sequencing vs additional sequencing'.
            slice_id (str): The ID of the slice to analyze.
            color (str): Color for the scatter plot markers. Default is 'blue'.
            s (int): Size of the scatter plot markers. Default is 15.
            o (str, optional): Path and filename for saving the image. If not provided, the image will not be saved.
        """
    adata1 = adata1[(adata1.obs[slice] == slice_id),]
    adata2 = adata2[(adata2.obs[slice] == slice_id),]
    s1_adata1 = adata1.obs.groupby(slice).size()
    s1_adata2 = adata2.obs.groupby(slice).size()
    p_adata1_list = []
    p_adata2_list = []
    for min_genes in min_genes_list:
        adata1_filtered = adata1.copy()
        adata2_filtered = adata2.copy()
        adata1_filtered = function.filter_cells(adata1_filtered, min_genes=min_genes)
        adata1_filtered = function.filter_genes(adata1_filtered, min_cells=min_cells)
        adata2_filtered = function.filter_cells(adata2_filtered, min_genes=min_genes)
        adata2_filtered = function.filter_genes(adata2_filtered, min_cells=min_cells)

        s2_adata1 = adata1_filtered.obs.groupby(slice).size()
        s2_adata2 = adata2_filtered.obs.groupby(slice).size()

        p_adata1 = s2_adata1 / s1_adata1
        p_adata2 = s2_adata2 / s1_adata2
        p_adata1_list.append(p_adata1)
        p_adata2_list.append(p_adata2)

    plt.figure(figsize=(image_width, image_height))
    if slice_id is None:
        raise ValueError("Please provide a valid slice_id.")

    p_adata1 = [p_adata1_list[i][slice_id] for i in range(len(min_genes_list))]
    p_adata2 = [p_adata2_list[i][slice_id] for i in range(len(min_genes_list))]

    plt.scatter(min_genes_list, p_adata1, label=f'{slice_id}', marker='o',color=color,s=s)
    plt.scatter(min_genes_list, p_adata2, label=f'{slice_id}', marker='^',color=color,s=s)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label=f'{slice_id}', markersize=8)]
    legend_elements.append(
        plt.Line2D([0], [0], marker='o', color='w', label='sequencing', markerfacecolor=color, markersize=8))
    legend_elements.append(
        plt.Line2D([0], [0], marker='^', color='w', label='additional sequencing', markerfacecolor=color, markersize=8))

    plt.legend(handles=legend_elements,loc='center left', bbox_to_anchor=(1, 0.5))
    if o is not None and isinstance(o, str):
        plt.savefig(o)
    plt.show()
