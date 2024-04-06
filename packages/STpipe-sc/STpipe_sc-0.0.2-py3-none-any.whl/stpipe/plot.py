import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from matplotlib.ticker import MultipleLocator, AutoLocator
import numpy as np
from matplotlib.lines import Line2D
from scipy.spatial import ConvexHull
from adjustText import adjust_text
from scipy.sparse import issparse
import pandas as pd
from itertools import groupby as it_groupby
from sklearn.utils.sparsefuncs import mean_variance_axis
from scipy.stats import gaussian_kde


def pca_variance_ratio(adata, color='brown', marker='o', markersize=4, figsize=(5, 4), dpi=360,
                       xlabel='Number of PCs', ylabel='Variance ratio', title=None, save=None, log=False, npc=20):
    """
        Plot the variance ratio of principal components obtained from PCA.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing PCA results.
            color (str): Color of the plot markers. Defaults to 'brown'.
            marker (str): Marker style for the plot. Defaults to 'o'.
            markersize (int): Size of the plot markers. Defaults to 4.
            figsize (tuple): Figure size in inches. Defaults to (5, 4).
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
            xlabel (str): Label for the x-axis. Defaults to 'Number of PCs'.
            ylabel (str): Label for the y-axis. Defaults to 'Variance ratio'.
            title (str): Title for the plot. Defaults to None.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            log (bool): Whether to plot the variance ratio in log scale. Defaults to False.
            npc (int): Number of principal components to include in the plot. Defaults to 20.
        """
    variance_ratio = adata.uns['pca']['variance_ratio'][:npc]
    plt.figure(figsize=figsize)
    if log:
        variance_ratio = np.log2(variance_ratio)
    x_values = range(1, len(variance_ratio) + 1)
    plt.plot(range(1, len(variance_ratio) + 1), variance_ratio, marker=marker, markersize=markersize, color=color)
    plt.xticks(x_values)
    x_major_locator = MultipleLocator(5)
    plt.gca().xaxis.set_major_locator(x_major_locator)
    plt.gca().yaxis.set_major_locator(AutoLocator())
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.title(title, fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    if save is not None:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)
    plt.show()


def spatial_bigcell_plot(adata, ncol=1, s=15, figsize=(7, 7), line_color='red', linewidth=1, xlabel='X', ylabel='Y',
                         title=None, save=None, dpi=360,
                         spatial_bigcell_key='membership', color_key='color', color_key_obs='leiden'):
    """
        Plot the spatial distribution of cells with highlighted spatial metacells.

        This function visualizes the spatial distribution of cells and highlights spatial metacells using convex hulls.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing spatial coordinates and membership information.
            ncol (int): Number of columns for the legend. Defaults to 1.
            s (int): Marker size for individual cells. Defaults to 15.
            figsize (tuple): Figure size in inches. Defaults to (7, 7).
            line_color (str): Color of the convex hull lines. Defaults to 'red'.
            linewidth (int): Line width of the convex hull lines. Defaults to 1.
            xlabel (str): Label for the x-axis. Defaults to 'X'.
            ylabel (str): Label for the y-axis. Defaults to 'Y'.
            title (str): Title for the plot. Defaults to None.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
            spatial_bigcell_key (str): Key in adata.obs representing spatial big cell membership. Defaults to 'membership'.
            color_key (str): Key in adata.obs representing the color of individual cells. Defaults to 'color'.
            color_key_obs (str): Key in adata.obs representing the color for the legend. Defaults to 'leiden'.
        """
    if 'spatial' in adata.obsm:
        coords = adata.obsm['spatial']
    elif 'x' in adata.obs and 'y' in adata.obs:
        coords = adata.obs[['x', 'y']].values
        print("x and y in adata.obs are being used. Please determine if they are cell coordinates")
    else:
        raise ValueError("Unable to find coordinate information, check the coordinate column in data")

    color_dict = dict(zip(adata.obs[color_key_obs], adata.obs[color_key]))

    membership = adata.obs[spatial_bigcell_key]
    plt.figure(figsize=figsize)
    categories = np.unique(adata.obs[color_key_obs])
    for category in categories:
        idx = adata.obs[color_key_obs] == category
        plt.scatter(coords[idx, 0], coords[idx, 1], color=color_dict[category], s=s)
    for i in set(membership):
        nodes = [j for j in range(len(membership)) if membership[j] == i]
        coords_subset = coords[nodes]
        if len(nodes) == 1:
            plt.scatter(coords_subset[0, 0], coords_subset[0, 1], color=adata.obs.iloc[nodes[0]]['color'], s=s)
        elif len(nodes) == 2:
            plt.plot(coords_subset[0, 0], coords_subset[0, 1], '-', color=line_color, linewidth=linewidth)
        else:
            hull = ConvexHull(coords_subset, qhull_options='QJ')
            for simplex in hull.simplices:
                plt.plot(coords_subset[simplex, 0], coords_subset[simplex, 1], '-', color=line_color,
                         linewidth=linewidth)

    legend_patches = [
        Line2D([0], [0], marker='o', color='w', label=label, markerfacecolor=color_dict[label], markersize=10) for
        label in categories]
    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0., frameon=False,
               ncol=ncol)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if save is not None:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)
    plt.show()


def violin(adata, groupby=None, feature='n_genes', n_rows=1, fig_size=(8, 6), save_path=None, dpi=360):
    """
        Generate violin plots to visualize the distribution of a feature across groups.

        This function generates violin plots to visualize the distribution of a specified feature across different groups
        in the dataset.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing the data.
            groupby (str or None): Key in adata.obs to group the data. If None, a single violin plot for the entire
                                    dataset will be generated. Defaults to None.
            feature (str): Feature to visualize. Defaults to 'n_genes'.
            n_rows (int): Number of rows in the plot grid. Defaults to 1.
            fig_size (tuple): Size of the figure in inches (width, height). Defaults to (8, 6).
            save_path (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
        """
    if groupby:
        unique_groups = adata.obs[groupby].unique()
        total_groups = len(unique_groups)
        groups_per_row = total_groups // n_rows + (1 if total_groups % n_rows != 0 else 0)

        fig, axs = plt.subplots(n_rows, groups_per_row, figsize=(fig_size[0] * groups_per_row, fig_size[1] * n_rows),
                                squeeze=False, sharey='all')
        for i, ax_row in enumerate(axs):
            start = i * groups_per_row
            end = min(start + groups_per_row, total_groups)
            current_groups = unique_groups[start:end]

            for j, group in enumerate(current_groups):
                group_data = adata.obs.loc[adata.obs[groupby] == group, feature]
                sns.violinplot(data=[group_data], ax=ax_row[j])

                ax_row[j].set_title('Distribution of ' + feature + ' for ' + group)

        for i in range(total_groups, n_rows * groups_per_row):
            fig.delaxes(axs.flatten()[i])

    else:
        fig, ax = plt.subplots(figsize=fig_size)
        sns.violinplot(y=adata.obs[feature], ax=ax)
        plt.title('Distribution of ' + feature)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=dpi)
    plt.show()


def variable_plot(adata, cols=('black', 'red'), figsize=(6, 6), save=None, log=False, s=1, annotate_genes=None,
                  legend_loc='best', dpi=360, anno_fontsize=10):
    """
        Generate a variable feature plot to visualize mean expression versus variance of genes.

        This function generates a variable feature plot to visualize the relationship between mean expression and variance
        of genes. Highly variable genes are highlighted in a different color.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing the data.
            cols (tuple): Colors to use for plotting non-highly variable genes and highly variable genes, respectively.
                          Defaults to ('black', 'red').
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (6, 6).
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            log (bool): Whether to use logarithmic scale for axes. Defaults to False.
            s (int): Marker size. Defaults to 1.
            annotate_genes (list or None): List of genes to annotate on the plot. Defaults to None.
            legend_loc (str): Location of the legend. Defaults to 'best'.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
            anno_fontsize (int): Font size for gene annotations. Defaults to 10.
        """
    mean_expression = adata.var['means']
    gene_variance = adata.var['variances_norm']
    highly_variable = adata.var['highly_variable']
    plt.figure(figsize=figsize)
    if log:
        plt.xscale('log')
        plt.yscale('log')
    plt.scatter(mean_expression[~highly_variable], gene_variance[~highly_variable], color=cols[0], alpha=0.5,
                label='Other Genes', s=s)
    plt.scatter(mean_expression[highly_variable], gene_variance[highly_variable], color=cols[1], alpha=0.5,
                label='Highly Variable Genes', s=s)

    if annotate_genes is not None:
        texts = []
        for gene in annotate_genes:
            if gene in adata.var_names:
                idx = np.where(adata.var_names == gene)[0][0]
                texts.append(
                    plt.text(mean_expression[idx], gene_variance[idx], gene, fontsize=anno_fontsize, ha='left', va='bottom'))

        adjust_text(texts, arrowprops=dict(arrowstyle="-", color='black', lw=0.5))

    plt.xlabel('Mean Expression')
    plt.ylabel('Variance')
    plt.title('Variable Feature Plot')
    plt.legend(loc=legend_loc)
    if save:
        plt.savefig(save, dpi=dpi, bbox_inches='tight')
    plt.show()


def plot_tsne(adata, by=None, s=5, cmap=None, savefig=None, dpi=360, figsize=(6, 6)):
    """
        Generate a t-SNE plot for visualizing high-dimensional data.

        This function generates a t-SNE plot to visualize high-dimensional data in two dimensions. Data points are represented
        as scatter points on the plot, with optional coloring by a specified category or gene expression level.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing the data.
            by (str or None): Name of the category column in adata.obs or a gene name in adata.var_names to color the plot
                              by. Defaults to None.
            s (int): Marker size for data points. Defaults to 5.
            cmap (str or None): Colormap name for coloring the plot. If None, 'viridis' colormap is used. Defaults to None.
            savefig (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (6, 6).
        """
    plt.figure(figsize=figsize)
    X_tsne = adata.obsm['X_tsne']

    if cmap is None:
        cmap = 'viridis'

    if by is not None:
        if by in adata.obs.columns:  # If `by` is a column in obs
            categories = np.unique(adata.obs[by])
            num_categories = len(categories)
            color_map = plt.get_cmap(cmap)
            colors = color_map(np.linspace(0, 1, num_categories))
            color_dict = {category: color for category, color in zip(categories, colors)}
            for category in categories:
                idx = adata.obs[by] == category
                plt.scatter(X_tsne[idx, 0], X_tsne[idx, 1], label=category, s=s, color=color_dict[category])
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        elif by in adata.var_names:  # If `by` is a gene
            expression_values = adata.raw[:, by].X.toarray().flatten() if issparse(adata.raw[:, by].X) else adata.raw[:, by].X.flatten()
            norm = mcolors.Normalize(vmin=expression_values.min(), vmax=expression_values.max())
            mapper = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
            colors = mapper.to_rgba(expression_values)
            plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=colors, s=s, edgecolors='none')
            cbar = plt.colorbar(mapper,label=by)
            cbar.set_label(by, rotation=270, labelpad=20)

    else:
        plt.scatter(X_tsne[:, 0], X_tsne[:, 1], s=s, edgecolors='none', c=cmap)

    plt.xlabel('tSNE1')
    plt.ylabel('tSNE2')

    if by is not None:
        plt.title(by)
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False,
                    labelleft=False)
    if savefig is not None:
        plt.savefig(savefig, dpi=dpi, bbox_inches='tight')

    plt.show()


def plot_marker_heatmap(cdata, use_raw=True, genes=[], groupby='leiden', z_score=None, figsize=(10, 10), vmin=None,
                        vmax=None, save=None, cmap='viridis', standard_scale=None, rotation=0, dpi=360):
    """
        Generate a marker heatmap plot for visualizing gene expression across cell clusters.

        This function generates a marker heatmap plot to visualize the expression of marker genes across different cell
        clusters. Each row in the heatmap represents a marker gene, and each column represents a cell cluster. The color
        intensity of each cell in the heatmap indicates the expression level of the corresponding marker gene in the
        respective cell cluster.

        Parameters:
            cdata (anndata.AnnData): An AnnData object containing the data.
            use_raw (bool): Whether to use raw.X instead of .X for gene expression. Defaults to True.
            genes (list): List of marker genes to include in the heatmap. Defaults to an empty list.
            groupby (str): Name of the category column in cdata.obs to group cells by. Defaults to 'leiden'.
            z_score (int or None): Whether to z-score normalize the expression values. If None, no normalization is applied.
                                   Defaults to None.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (10, 10).
            vmin (float or None): Minimum value for color normalization. If None, the minimum value in the data is used.
                                  Defaults to None.
            vmax (float or None): Maximum value for color normalization. If None, the maximum value in the data is used.
                                  Defaults to None.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            cmap (str): Colormap name for coloring the heatmap. Defaults to 'viridis'.
            standard_scale (int or None): Whether to standard scale the expression values along the rows or columns. If None,
                                          no scaling is applied. Defaults to None.
            rotation (int): Rotation angle for cluster labels on the x-axis. Defaults to 0.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.

        Returns:
            (seaborn.matrix.ClusterGrid): A ClusterGrid object representing the marker heatmap plot.
        """
    expression_data = []
    for gene in genes:
        if use_raw:
            gene_data = cdata.raw[:, gene].X
        else:
            gene_data = cdata[:, gene].X

        if issparse(gene_data):
            gene_data = gene_data.toarray()

        expression_data.append(gene_data)

    expression_data = np.array(expression_data)
    expression_data = np.squeeze(expression_data)
    categories = cdata.obs[groupby]

    sorted_indices = np.argsort(categories)
    expression_data = expression_data[:, sorted_indices]
    sorted_categories = categories[sorted_indices]
    expression_data_df = pd.DataFrame(expression_data, index=genes, columns=sorted_categories)

    cmap0 = sns.color_palette("hls", len(sorted_categories.unique()))
    category_to_color = dict(zip(sorted_categories.unique(), cmap0))
    col_colors = [category_to_color[category] for category in sorted_categories]

    g = sns.clustermap(expression_data_df, cmap=cmap, row_cluster=False, col_cluster=False, col_colors=col_colors,
                       xticklabels=False, z_score=z_score, figsize=figsize, vmax=vmax, vmin=vmin,
                       standard_scale=standard_scale)
    g.fig.subplots_adjust(right=0.7)
    g.ax_cbar.set_position((0.75, .2, .03, .4))
    g.ax_heatmap.yaxis.set_ticks_position('left')
    borders = np.cumsum([0] + [sum(1 for i in g) for k, g in it_groupby(col_colors)])
    for b0, b1, category in zip(borders[:-1], borders[1:], sorted_categories.unique()):
        g.ax_col_colors.text((b0 + b1) / 2, 1.06, category, color='black', ha='center', va='bottom',
                             transform=g.ax_col_colors.get_xaxis_transform(), rotation=rotation)

    for border in borders[1:-1]:
        g.ax_heatmap.axvline(border, color='grey', linewidth=0.5)

    if save:
        g.savefig(save, dpi=dpi, bbox_inches='tight')
    return g


def _df(cdata, groupby='leiden', genes=[]):
    groups = sorted(cdata.obs[groupby].unique())
    data = []

    for gene in genes:
        for group in groups:
            cells = cdata.obs.index[cdata.obs[groupby] == group]
            expression_values = cdata[cells, cdata.var_names == gene].X

            if issparse(expression_values):
                expression_values = np.expm1(expression_values)
                mean, var = mean_variance_axis(expression_values, axis=0)
                mean = np.squeeze(mean)
                pct = np.mean(expression_values > 0)
            else:
                expression_values = np.expm1(expression_values)
                mean = np.mean(expression_values)
                pct = np.mean(expression_values > 0)

            data.append([gene, group, pct, mean])

    df = pd.DataFrame(data, columns=['genes', 'group', 'pct', 'mean'])
    return df


def plot_marker_dotplot(cdata, genes=[], groupby='leiden', figsize=(10, 8), vmin=0, vmax=3,
                        cmap='viridis', rotation=0, save=None, dpi=360):
    """
        Generate a marker dot plot to visualize gene expression across cell clusters.

        This function generates a marker dot plot to visualize the expression of marker genes across different cell
        clusters. Each dot in the plot represents a cell cluster, and the color and size of the dot indicate the average
        expression level and percentage of cells expressing the marker gene, respectively.

        Parameters:
            cdata (anndata.AnnData): An AnnData object containing the data.
            genes (list): List of marker genes to include in the dot plot.
            groupby (str): Name of the category column in cdata.obs to group cells by. Defaults to 'leiden'.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (10, 8).
            vmin (float): Minimum value for color normalization. Defaults to 0.
            vmax (float): Maximum value for color normalization. Defaults to 3.
            cmap (str): Colormap name for coloring the dots. Defaults to 'viridis'.
            rotation (int): Rotation angle for cluster labels on the x-axis. Defaults to 0.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
        """
    sorted_genes = genes
    df = _df(cdata, groupby=groupby, genes=genes)
    plt.figure(figsize=figsize)
    groups = sorted(cdata.obs[groupby].unique())
    percent_bins = [0.1, 0.3, 0.5, 0.7, 0.9]
    sizes = [1, 4, 7, 10, 13]

    for index, row in df.iterrows():
        x = list(groups).index(row['group'])
        y = sorted_genes.index(row['genes'])

        size = 0.01
        for i in range(len(percent_bins)):
            if row['pct'] >= percent_bins[i]:
                size = sizes[i]

        plt.scatter(x, y, s=size * 10, c=row['mean'], cmap=cmap, alpha=0.6, vmin=vmin, vmax=vmax)

    plt.colorbar(label='Average Expression', shrink=0.4, pad=0.03)

    plt.scatter([], [], s=1 * 10, label='10%', color='black')
    plt.scatter([], [], s=4 * 10, label='30%', color='black')
    plt.scatter([], [], s=7 * 10, label='50%', color='black')
    plt.scatter([], [], s=10 * 10, label='70%', color='black')
    plt.scatter([], [], s=13 * 10, label='90%', color='black')
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Percent\nExpressed', loc='center left',
               bbox_to_anchor=(0.86, 0.5),bbox_transform=plt.gcf().transFigure)

    plt.xticks(range(len(groups)), groups, rotation=rotation)

    plt.yticks(range(len(sorted_genes)), sorted_genes)
    if save:
        plt.savefig(save, dpi=dpi, bbox_inches='tight')
    plt.tight_layout()
    plt.show()


def plot_spatial(adata, by=None, s=5, cmap=None, savefig=None, dpi=360, figsize=(6, 6),
                 tiff=None, coord='spatial', title=None, legend=False, categorical=False, legend_title=True):
    """
        Plot spatial information from Stereo-seq data.

        This function visualizes spatial information from Stereo-seq data. It can display cell
        coordinates on an image, with the option to color cells based on a specified category or gene expression level.

        Parameters:
            adata (anndata.AnnData): An AnnData object containing the spatial data.
            by (str or None): Name of the category column in adata.obs to group cells by, or name of the gene for coloring
                              cells based on gene expression. Defaults to None.
            s (float): Size of the markers representing cells. Defaults to 5.
            cmap (str or None): Colormap for coloring cells. Defaults to None, which uses the 'viridis' colormap.
            savefig (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (6, 6).
            tiff (str or None): Name of the TIFF file in adata.uns['spatial'] to overlay on the plot. Defaults to None.
            coord (str): Key in adata.obsm containing the spatial coordinates. Defaults to 'spatial'.
            title (str or None): Title for the plot. Defaults to None.
            legend (bool): Whether to display the legend. Defaults to False.
            categorical (bool): If True, color cells based on the specified category. If False, color cells based on gene
                                expression. Defaults to False.
            legend_title (bool): Title for the legend. Defaults to True.
        """
    plt.figure(figsize=figsize)
    coord = adata.obsm[coord]

    if tiff is not None and tiff in adata.uns['spatial']:
        tiff_data = adata.uns['spatial'][tiff]['images']['hires']
        plt.imshow(tiff_data)

    if cmap is None:
        cmap = 'viridis'

    if by is not None:
        if by in adata.obs.columns:  # column in obs
            if categorical:
                categories = np.unique(adata.obs[by])
                num_categories = len(categories)
                color_map = plt.get_cmap(cmap)
                colors = color_map(np.linspace(0, 1, num_categories))
                color_dict = {category: color for category, color in zip(categories, colors)}
                for category in categories:
                    idx = adata.obs[by] == category
                    plt.scatter(coord[idx, 0], coord[idx, 1], label=category, s=s, color=color_dict[category])
                    if legend:
                        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            else:
                expression_values = adata.obs_vector(by)
                color_map = plt.get_cmap(cmap)
                plt.scatter(coord[:, 0], coord[:, 1], c=expression_values, cmap=color_map, s=s, edgecolors='none')
                cbar = plt.colorbar()
                if legend_title:
                    cbar.set_label(by, rotation=270, labelpad=20)

        elif by in adata.var_names:  # If `by` is a gene
            expression_values = adata[:, by].X.toarray().flatten() if issparse(adata[:, by].X) else adata[:, by].X.flatten()
            plt.scatter(coord[:, 0], coord[:, 1], c=expression_values, cmap=cmap, s=s, edgecolors='none')
            if legend:
                cbar = plt.colorbar()
                ax_pos = plt.gca().get_position()
                cbar.ax.set_position([ax_pos.x1 + 0.01, ax_pos.y0, 0.02, ax_pos.height])
                if legend_title:
                    cbar.set_label(by, rotation=270, labelpad=20)

    else:
        plt.scatter(coord[:, 0], coord[:, 1], s=s, edgecolors='none', c=cmap)

    plt.xlabel('X')
    plt.ylabel('Y')

    plt.title(title)
    plt.xlim([np.min(coord[:, 0]) - 1, np.max(coord[:, 0]) + 1])
    plt.ylim([np.min(coord[:, 1]) - 1, np.max(coord[:, 1]) + 1])
    ax = plt.gca()
    ax.set_aspect(1)
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False,
                    labelleft=False)
    if savefig is not None:
        plt.savefig(savefig, dpi=dpi, bbox_inches='tight')

    plt.show()


def plot_labeltransfer_score_distribution(adata_transfer, bar_color='skyblue', figsize=(8, 6), save=None, xrotation=0, dpi=360):
    """
        Plot the distribution of label transfer maximum scores.

        This function plots the distribution of maximum scores obtained during the label transfer process.

        Parameters:
            adata_transfer (anndata.AnnData): An AnnData object containing the label transfer results.
            bar_color (str): Color of the bars in the histogram. Defaults to 'skyblue'.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (8, 6).
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            xrotation (float): Rotation angle for x-axis tick labels. Defaults to 0.
            dpi (int): Dots per inch for the figure resolution. Defaults to 360.
        """
    num_bins = 10
    score_min = 0
    score_max = 1
    bin_edges = np.linspace(score_min, score_max, num_bins + 1)

    hist, _ = np.histogram(adata_transfer.obs['max_score'], bins=bin_edges)

    plt.figure(figsize=figsize)
    plt.bar(range(num_bins), hist, align='center', color=bar_color, edgecolor='black')

    plt.title('Distribution of labeltransfer max scores')
    plt.xlabel('Score Bins')
    plt.ylabel('Frequency')

    plt.xticks(range(num_bins), [f'{bin_edges[i]:.2f}-{bin_edges[i + 1]:.2f}' for i in range(num_bins)],
               rotation=xrotation)

    if save:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)

    plt.show()


def plot_labeltransfer_score_violin(adata_transfer, groupby='id', inner=None, save=None, figsize=(8,5),xrotation=90,xha='right',  color='blue'):
    """
        Plot a violin plot of label transfer maximum scores.

        This function plots a violin plot of maximum scores obtained during the label transfer process grouped by a specified category.

        Parameters:
            adata_transfer (anndata.AnnData): An AnnData object containing the label transfer results.
            groupby (str): Key in adata_transfer.obs specifying the category by which to group the scores. Defaults to 'id'.
            inner (str or None): Type of data representation inside the violins. Defaults to None.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (8, 5).
            xrotation (int): Rotation angle for x-axis tick labels. Defaults to 90.
            xha (str): Horizontal alignment of x-axis tick labels. Defaults to 'right'.
            color (str): Color of the violins. Defaults to 'blue'.
        """
    plt.figure(figsize=figsize)
    sns.violinplot(x=groupby, y='max_score', data=adata_transfer.obs, inner=inner, color=color)

    plt.ylabel('Max Score')
    plt.xlabel(None)

    plt.xticks(rotation=xrotation,ha=xha)
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=300)
    plt.show()


def plot_cellcount_between_ref_query(adata_query, adata_ref ,key1='labeltransfer_celltype', key2='celltype', figsize=(12, 5),
                                     xrotation=45, xha='right', save=None, title1='scRNA-seq', title2='Stereo-seq',dpi=360):
    """
        Plot cell count comparison between reference and query datasets.

        This function plots a bar chart comparing the cell counts of different cell types between a reference dataset
        and a query dataset.

        Parameters:
            adata_query (anndata.AnnData): An AnnData object representing the query dataset.
            adata_ref (anndata.AnnData): An AnnData object representing the reference dataset.
            key1 (str): Key in adata_query.obs representing the cell type information. Defaults to 'labeltransfer_celltype'.
            key2 (str): Key in adata_ref.obs representing the cell type information. Defaults to 'celltype'.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (12, 5).
            xrotation (int): Rotation angle for x-axis tick labels. Defaults to 45.
            xha (str): Horizontal alignment of x-axis tick labels. Defaults to 'right'.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            title1 (str): Title for the query dataset plot. Defaults to 'scRNA-seq'.
            title2 (str): Title for the reference dataset plot. Defaults to 'Stereo-seq'.
            dpi (int): Dots per inch for the saved figure. Defaults to 360.
        """
    adata_celltype_counts = adata_query.obs[key1].value_counts()
    bdata_celltype_counts = adata_ref.obs[key2].value_counts()
    all_celltypes = set(adata_celltype_counts.index) | set(bdata_celltype_counts.index)
    all_celltypes = sorted(all_celltypes)

    fig, axs = plt.subplots(2, 1, figsize=figsize)
    axs[0].bar(all_celltypes, [adata_celltype_counts.get(celltype, 0) for celltype in all_celltypes], color='skyblue')
    axs[0].set_title(title2)
    axs[0].set_ylabel('Cell Count')
    axs[0].set_xticks([])

    axs[1].bar(all_celltypes, [bdata_celltype_counts.get(celltype, 0) for celltype in all_celltypes], color='salmon')
    axs[1].set_title(title1)
    axs[1].set_ylabel('Cell Count')

    plt.xticks(rotation=xrotation, ha=xha)
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)
    plt.show()


def plot_moran(moran1, moran2, figsize=(5, 5), s=2, anno=None, save=None, dpi=360):
    """
        Plot Moran scatter plot between two datasets.

        This function plots a Moran scatter plot between two datasets. It visualizes the Moran scores of common genes
        shared between the two datasets.

        Parameters:
            moran1 (pandas.Series): Moran scores for the first dataset.
            moran2 (pandas.Series): Moran scores for the second dataset.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (5, 5).
            s (int): Marker size. Defaults to 2.
            anno (list or None): List of gene names to annotate on the plot. If None, no annotations are added. Defaults to None.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the saved figure. Defaults to 360.
        """
    common_genes = moran1.index.intersection(moran2.index)
    moran1_common = moran1.loc[common_genes]
    moran2_common = moran2.loc[common_genes]

    plt.figure(figsize=figsize)
    plt.scatter(moran1_common, moran2_common, s=s)
    texts = []
    if anno is not None:
        for gene in anno:
            texts.append(plt.text(moran1_common[gene], moran2_common[gene], gene))

        adjust_text(texts, arrowprops=dict(arrowstyle="-", color='black', lw=0.5))

    plt.xlabel('moran_scRNA-seq')
    plt.ylabel('moran_Spatial')
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)
    plt.show()


def metacell_size(adata, color='skyblue', bins=20, save=None, dpi=360, figsize=(8, 6)):
    """
        Plot the distribution of metacell sizes.

        This function plots a histogram of metacell sizes along with a kernel density estimate (KDE) curve.

        Parameters:
            adata (anndata.AnnData): Annotated data object containing metacell information.
            color (str): Color of the histogram bars. Defaults to 'skyblue'.
            bins (int): Number of bins for the histogram. Defaults to 20.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the saved figure. Defaults to 360.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (8, 6).
        """
    membership_sizes = adata.uns['membership_sizes']

    plt.figure(figsize=figsize)
    plt.hist(membership_sizes, bins=bins, color=color, edgecolor='black', density=True)
    kde = gaussian_kde(membership_sizes)
    x = np.linspace(min(membership_sizes), max(membership_sizes), 1000)
    plt.plot(x, kde(x), color='red', linestyle='-', linewidth=1)
    plt.xlabel('Membership Size')
    plt.ylabel('Density')
    plt.title('Distribution of metacell sizes')
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)

    plt.show()


def metacell_purity(adata, bins=20, color='skyblue', save=None, dpi=360, celltype='leiden', figsize=(8, 6)):
    """
        Plot the distribution of metacell purity.

        This function calculates the purity of each metacell based on the predominant cell type and plots
        the distribution of purities as a histogram along with a kernel density estimate (KDE) curve.

        Parameters:
            adata (anndata.AnnData): Annotated data object containing metacell information.
            bins (int): Number of bins for the histogram. Defaults to 20.
            color (str): Color of the histogram bars. Defaults to 'skyblue'.
            save (str or None): File path to save the plot. If None, the plot is not saved. Defaults to None.
            dpi (int): Dots per inch for the saved figure. Defaults to 360.
            celltype (str): Column name representing the cell type information in the AnnData object. Defaults to 'leiden'.
            figsize (tuple): Size of the figure in inches (width, height). Defaults to (8, 6).
        """
    membership = adata.obs['membership']
    leiden = adata.obs[celltype]
    membership_categories = membership.unique()
    purities = []
    for category in membership_categories:
        membership_leiden_counts = leiden[membership == category].value_counts()
        max_count = membership_leiden_counts.max()
        total_count = membership_leiden_counts.sum()
        purity = max_count / total_count

        purities.append(purity)

    plt.figure(figsize=figsize)
    plt.hist(purities, bins=bins, color=color, edgecolor='black', density=True)
    plt.xlabel('Purity')
    plt.ylabel('Density')
    plt.title('Distribution of metacell purity')

    kde = gaussian_kde(purities)
    x = np.linspace(min(purities), max(purities), 1000)
    plt.plot(x, kde(x), color='red', linestyle='-', linewidth=1)
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=dpi)
    plt.show()