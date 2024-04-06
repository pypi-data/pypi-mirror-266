import numpy as np
import os
import pandas as pd
import pymc as pm
import matplotlib.pyplot as plt
import seaborn as sns
import tqdm as tqdm
import requests
from io import BytesIO
import tempfile

RANDOM_SEED = 8927
rng = np.random.default_rng(RANDOM_SEED)

import random


class SimInit:
    """
    Manages initiation of simulations based on user-defined parameters.

    This class serves as the starting point for simulations, taking user-specified parameters
    and saving them into an HDF5 (.h5) file for persistent storage. It acts as a base class,
    passing the initialized parameters to inherited classes responsible for executing
    the actual simulation tasks.

    Parameters are encapsulated in an HDF5 file due to its efficiency in handling large
    datasets and its hierarchical structure, which is suitable for complex simulations.

    The class is designed to be inherited by specific simulation classes, which will
    implement the detailed logic necessary for performing the simulation based on the
    initial parameters.
    
    parameters
    ==========
    targetNum: int
    geneNum: int
    effectSgRNA: int, 
        between 0 to 5
    getData: bool,
        data load to memeory
    return
    ======
    dfSubset: table
    effective_sgRNA_flat: list
    
    """
    def __init__(self, targetNum, geneNum, effectSgRNA, getData):
        self.targetNum = targetNum
        self.geneNum = geneNum
        self.effectSgRNA = effectSgRNA
        self.getData = getData
        

    #reading files stay in memory (google colab)
    def download_data_file_and_read(self,url, data_key):
        """
        Downloads a file from the given URL to a named temporary file and reads it.
        """
        with requests.get(url, stream=True) as r:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                
                # The file needs to be closed before reading
                tmp_file_name = tmp_file.name

        # Now you can read from the downloaded file
        try:
            dfinit = pd.read_hdf(tmp_file_name, key=data_key)
        except Exception as e:
            raise IOError(f"Cannot read HDF5 data: {e}")
        # Optionally, if you'd like to clean up immediately after reading
        # os.unlink(tmp_file_name)
        return dfinit
    
    def loading_data(self):
        if self.geneNum is None or self.targetNum is None or self.targetNum > self.geneNum or self.targetNum==0:
            raise ValueError("Invalid or missing parameters. Please ensure targetNum is not 0, parameters are not None, and targetNum is less than or equal to geneNum.") 
        else:
            data_key = 'dataset' 
            if self.getData:
                # Define the URL of the raw data file on GitHub
                url = "https://raw.githubusercontent.com/gkanfer/AIPySdeAnalyzer/main/datasgRNA.h5"
                print(f"Downloading data file from {url}")
                dfinit = self.download_data_file_and_read(url,data_key)
            else:
                file_path = 'datasgRNA.h5'                
                dfinit = pd.read_hdf(file_path, key=data_key)
            df = dfinit.iloc[8:,:]
            unique_genes = df['gene'].unique()
            selected_genes = random.sample(list(unique_genes), self.geneNum)  # Randomly select
            dfSubset = df[df['gene'].isin(selected_genes)]
            target_genepool = random.sample(list(selected_genes), self.targetNum)
            effective_sgRNA = [dfSubset.loc[dfSubset['gene'] == gene,'sgID'].to_list()[0:self.effectSgRNA] for gene in set(target_genepool)]
            effective_sgRNA_flat = [item for sublist in effective_sgRNA for item in sublist]
            return dfSubset, effective_sgRNA_flat
        
        
def download_file(url, local_filename):
    """
    Downloads a file from the given URL and saves it locally.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def ensure_data_file():
    """
    Ensures the required datasgRNA.h5 file is available.
    """
    data_filename = "datasgRNA.h5"
    data_path = os.path.join(os.path.expanduser("~"), data_filename)
    
    # Check if the file doesn't already exist
    if not os.path.exists(data_path):
        print(f"Downloading {data_filename}...")
        url = "https://raw.githubusercontent.com/gkanfer/AIPySdeAnalyzer/main/datasgRNA.h5"
        download_file(url, data_path)
    else:
        print(f"{data_filename} already exists.")
    
    return data_path