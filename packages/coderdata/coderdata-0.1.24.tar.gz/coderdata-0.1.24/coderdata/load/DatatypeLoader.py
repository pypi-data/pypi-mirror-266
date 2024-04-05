# coderdata/load/DatatypeLoader.py


import pandas as pd
import gzip
import os

class DatatypeLoader:
    def __init__(self, datatype, data_directory="."):
        """
        Initialize the loader for a specific datatype across various datasets.

        Parameters
        ----------
        datatype : str
            The type of data to load (e.g., 'transcriptomics', 'proteomics').
        data_directory : str
            The directory where data files are stored.
        """
        self.datatype = datatype
        self.data_directory = data_directory
        self.datasets = {}
        self.load_datatype()

    def load_datatype(self):
        """
        Load all files corresponding to the specified datatype from the data directory.
        """
        print("Loading data for datatype:", self.datatype)
        for file_name in os.listdir(self.data_directory):
            if self.datatype in file_name and file_name.endswith(('.csv', '.csv.gz', '.tsv', '.tsv.gz')):
                dataset_prefix = file_name.split('_')[0]
                file_path = os.path.join(self.data_directory, file_name)
                self.datasets[dataset_prefix] = self.load_file(file_path)
    
    @staticmethod
    def load_file(file_path):
        """
        Load a file into a pandas DataFrame.

        Parameters
        ----------
        file_path : str
            The path to the file to load.

        Returns
        -------
        pd.DataFrame
            The loaded data as a pandas DataFrame.
        """
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt') as file:
                return pd.read_csv(file, delimiter=DatatypeLoader.determine_delimiter(file_path))
        else:
            return pd.read_csv(file_path, delimiter=DatatypeLoader.determine_delimiter(file_path))

    @staticmethod
    def determine_delimiter(file_path):
        """
        Determine the delimiter of a file based on its extension.

        Parameters
        ----------
        file_path : str
            The path to the file.

        Returns
        -------
        str
            The delimiter character.
        """
        return '\t' if '.tsv' in file_path else ','

    def info(self):
        """
        Print information about the loaded datasets.
        """
        for dataset, df in self.datasets.items():
            print(f"Dataset {dataset} - Rows: {df.shape[0]}, Columns: {df.shape[1]}")
