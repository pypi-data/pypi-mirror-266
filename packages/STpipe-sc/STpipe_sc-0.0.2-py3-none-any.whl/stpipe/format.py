import os
import re
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import anndata
from scipy.sparse import csr_matrix
from shapely.geometry import MultiPoint

class FileProcessor:
    def __init__(self, directory='./', p=6, extension='.csv', header='infer', sep=','):
        """
            Initialize a FileProcessor object.

            Parameters:
                directory (str, optional): Directory path containing the files to process. Default is './'.
                p (int, optional): Number of parallel processes to use. Default is 6.
                extension (str, optional): File extension to filter files. Default is '.csv'.
                header (str, optional): Row index to use as the header. Default is 'infer'.
                sep (str, optional): Delimiter for reading and writing CSV files. Default is ','.

            Warning:
                This class may modify source files during processing. It is recommended to make a
                backup of the files before use.
            """
        self.directory = directory
        self.p = p
        self.extension = extension
        self.header = header
        self.sep = sep

    def _process_files_with_executor(self, process_function, process_args):
        with ProcessPoolExecutor(max_workers=self.p) as executor:
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    if file.endswith(self.extension):
                        filepath = os.path.join(root, file)
                        executor.submit(process_function, filepath, *process_args, header=self.header, sep=self.sep)

    def add_slice_number(self, slice_pattern=r'_([0-9]+)_'):
        """
            Add slice numbers to the last column of the file based on a given pattern.

            This method adds slice numbers to the last column of each file in the specified directory
            based on the provided pattern. It uses parallel processing with the specified number of
            processes.

            Parameters:
                slice_pattern (str): Regular expression pattern to extract slice numbers from filenames.
                                           Default is r'_([0-9]+)_'.

            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """


        self._process_files_with_executor(self._add_slicenumber, (slice_pattern,))

    def delete_rows(self, column_index=0, value_to_delete=None):
        """
            Delete rows from CSV files based on a specific column's value.

            This method iterates through CSV files in the specified directory and deletes rows from each file where the value
            in the specified column matches the given value_to_delete.

            Parameters:
                column_index (int): Index of the column to consider for deletion. Default is 0.
                value_to_delete (str or None): The value to be matched in the specified column for row deletion.
                                                     If None, rows are deleted where the column value is empty.
                                                     Default is None.
            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """
        self._process_files_with_executor(self._delete_rows, (column_index, value_to_delete))

    def delete_cols(self, column_indices):
        """
            Delete columns from CSV files based on a list of column indices.

            This method iterates through CSV files in the specified directory and deletes the specified columns from each file.

            Parameters:
                column_indices (list): List of column indices to be deleted from each CSV file.

            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """
        self._process_files_with_executor(self._delete_cols, (column_indices,))

    def rename_cols(self, column_mapping):
        """
            Rename columns in CSV files based on a dictionary mapping of old column names to new column names.

            This method iterates through CSV files in the specified directory and renames columns according to the provided mapping.

            Parameters:
                column_mapping (dict): Dictionary mapping old column names to new column names for renaming.

            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """
        self._process_files_with_executor(self._rename_cols, (column_mapping,))

    def reorder_cols(self, column_order):
        """
            Reorder columns in CSV files based on a specified list of column names.

            This method iterates through CSV files in the specified directory and reorders columns according to the provided order.

            Parameters:
                column_order (list): List of column names specifying the desired order of columns.

            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """
        self._process_files_with_executor(self._reorder_cols, (column_order,))

    def to_anndata(self):
        """
            Convert files into AnnData objects and save as HDF5 files.

            This method reads files in the specified directory, processes the data, converts it into AnnData objects, and saves each AnnData object as a separate HDF5 file with the same name as the input file.

            Returns:
                None (NoneType): This method operates directly on the files in the specified directory. It does not return any value upon completion.
            """
        self._process_files_with_executor(self._to_anndata, ())

    def _add_slicenumber(self, filepath, slice_pattern,sep,header):
        match = re.search(slice_pattern, filepath)
        if match:
            number = match.group(1)
            df = pd.read_csv(filepath, sep=sep, header=header)
            df.iloc[:, -1] = df.iloc[:, -1].apply(lambda x: str(x) + '-' + number)
            df.to_csv(filepath, sep=sep, index=False)

    def _delete_rows(self, filepath, column_index, value_to_delete,sep,header):
        df = pd.read_csv(filepath, sep=sep, header=header)
        df = df[df.iloc[:, column_index] != value_to_delete]
        df.to_csv(filepath, sep=sep,index=False)

    def _delete_cols(self, filepath,column_indices,sep,header):
        df = pd.read_csv(filepath ,sep=sep ,header=header )
        df.drop(columns=df.columns[column_indices], inplace=True)
        df.to_csv(filepath ,sep=sep ,index=False )

    def _rename_cols(self ,filepath ,column_mapping,sep,header):
        df = pd.read_csv(filepath ,sep=sep ,header=header )
        if column_mapping:
            df.rename(columns=column_mapping ,inplace=True )
        df.to_csv(filepath ,sep=sep ,index=False )

    def _reorder_cols(self ,filepath ,column_order,sep,header):
        df = pd.read_csv(filepath ,sep=sep ,header=header )
        if column_order:
            df = df[column_order]
        df.to_csv(filepath ,sep=sep ,index=False )

    def _to_anndata(self, filepath,sep,header):
        df = pd.read_csv(filepath, sep=sep, header=header)
        expr_matrix = df.pivot_table(values='MIDCount', index='CellID', columns='geneID', fill_value=0)
        sparse_matrix = csr_matrix(expr_matrix.to_numpy())

        def calculate_centroid(group):
            points = group[['x', 'y']].values
            centroid = MultiPoint(points).centroid
            return pd.Series({'x': centroid.x, 'y': centroid.y})

        obs = df.groupby('CellID').apply(calculate_centroid)
        adata = anndata.AnnData(X=sparse_matrix, obs=obs)
        adata.obsm['spatial'] = obs[['x', 'y']].to_numpy()
        filename, extension = os.path.splitext(filepath)
        new_filepath = filename + '.h5ad'
        adata.write(new_filepath)

    def merge_h5ad(self, join="outer", index_unique=None, **kwargs):
        """
            Merge multiple h5ad files into a single AnnData object.

            This method searches for h5ad files in the specified directory, reads them using concurrent processing, and
            then merges them into a single AnnData object.

            Parameters:
                join (str, optional): Type of join operation for merging. Options include "outer", "inner".
                                  Default is "outer".
                index_unique (str, optional): If provided, specifies how to handle index values. Default is None.
                **kwargs (typing.Any): Additional keyword arguments to be passed to the `anndata.concat` function.

            Returns:
                combined_ad (AnnData): The merged AnnData object containing data from multiple h5ad files.
            """
        h5ad_files = []
        with ProcessPoolExecutor(max_workers=self.p) as executor:
            futures = []
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    if file.endswith('.h5ad'):
                        filepath = os.path.join(root, file)
                        future = executor.submit(anndata.read_h5ad, filepath)
                        futures.append(future)
            for future in futures:
                h5ad_files.append(future.result())
        if h5ad_files:
            combined_ad = anndata.concat(h5ad_files, join=join, index_unique=index_unique, **kwargs)
            return combined_ad
        else:
            print("No h5ad files found in the directory")
            return None
