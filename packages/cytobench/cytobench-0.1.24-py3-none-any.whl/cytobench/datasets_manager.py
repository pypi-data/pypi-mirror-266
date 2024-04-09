import os
import requests

import logging

import pandas as pd
import numpy as np

import joblib
import json

import scipy

# if the user doesn't specify a folder with the dataset name,
# this will be used as default directory (with respect to where the script is being called from)
default_datasets_directory = 'cytobench-datasets'

# minimum files that should be contained in the dataset directory
default_datasets_files = ['counts.mtx', 'genes.csv', 'metadata.csv']


def get_dataset_path(dataset):
    
    '''
    deconvolve name from identifier and checks that the expected files are there
    dataset: can be either a string or path
    '''
    
    if os.path.isabs(dataset) or os.sep in dataset:
        local_path = dataset
    else:
        # if it's just a dataset name, use the default directory
        local_path = os.path.join(default_datasets_directory, dataset)
        
    assert os.path.exists(local_path), 'dataset not found; you may want to download it first with download_dataset'
    
    # check that the minimum files are present and it's not just a random directory    
    for file in default_datasets_files:
        
        file_path = os.path.join(local_path, file)
        assert os.path.exists(file_path), f'{file_path} file not found'
        
    return local_path


def binarize_dataset(local_path):
    
    '''
    run the first time to binarize the data
    '''
    
    # Load the sparse matrix and convert it back to a Numpy array
    counts = scipy.io.mmread(os.path.join(local_path, 'counts.mtx')).tocsr()

    # Load the list data from the CSV
    genes = pd.read_csv(os.path.join(local_path, 'genes.csv'), header=None).squeeze('columns').tolist()

    # Load the Pandas DataFrame from the CSV file
    metadata = pd.read_csv(os.path.join(local_path, 'metadata.csv'), low_memory=False)
    
    # Dump in binary file
    return joblib.dump((counts, genes, metadata), os.path.join(local_path, 'binaries.joblib'))
    

def load_dataset(dataset, split = 0, internal = True, return_dense = True):
    
    '''
    Loads a dataset and returns it in the form counts, genes, metadata
    In general a dataset will be returned splitted (ie. only certain cells will be returned),
    unless split = -1, in which case the full dataset will be returned
    Also the data is by default returned as a dense matrix, whereas it is stored in disk as sparse
    The "internal" flag serves to validate if the part of the dataset returned is the one meant for training (True) or test (False)
    '''
    
    # get dataset path in disk
    local_path = get_dataset_path(dataset)
    
    # compile dataset binaries if they don't already exist in disk
    binary_path = os.path.join(local_path, 'binaries.joblib')
    
    if not os.path.exists(binary_path):
        logging.info('Binaries of dataset not found, generate and store...')
        binarize_dataset(local_path)
        
    # load full dataset from binaries
    counts, genes, metadata = joblib.load(binary_path)
    
    # check split in range (approx)
    assert split < len(metadata['cytosplit'].unique()), "split out of range with respect to selected database"
    
    # count matrix is stored as sparse; make it dense if this is the requested format
    if return_dense:
        counts = counts.toarray()
        
    # mask samples from current split or the complement according to internal
    mask = (metadata['cytosplit'] != split) == internal

    # return masked dataset
    return counts[mask], genes, metadata[mask]


def get_dataset_splits(dataset):
    
    '''
    Returns the total number of splits for the selected dataset
    '''
    
    counts, genes, metadata = load_dataset(dataset, split = -1, return_dense = False)
    
    return len(metadata['cytosplit'].unique())


def download_file(url, local_filename):
    
    '''
    FIX: remove or update
    '''
    
    # Ensure the local directory exists
    os.makedirs(os.path.dirname(local_filename), exist_ok=True)
    
    # Stream download to handle large files
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename


def download_dataset(dataset):
    
    '''
    FIX: for sure update
    '''

    assert dataset in ['tabula-muris-simple-droplet-v1'], 'dataset not found'

    mega = Mega()
    m = mega.login()

    genes_file = "https://mega.nz/file/Y0VCHTiL#-6RMTZh9ZWO4GkGJlEGl5hyyNDsHONSayN9aJ_cpl5I"
    metadata_file = "https://mega.nz/file/99d2WIwK#pXOP4j3REic1xhwe9Ms5ODpgO1BKrDwrwzDEaamrbcQ"
    counts_file = "https://mega.nz/file/1psUySSD#YQVpUULCXP605gW-RGt1SCbkpA18RwRK1rCN7PehNvs"

    logging.info("Downloading genes file...")

    local_dir = os.path.join(script_dir, 'cytobench-datasets')
    os.makedirs(local_dir, exist_ok=True)

    local_path = os.path.join(script_dir, 'cytobench-datasets', dataset + '-genes.csv')
    # download_file(genes_file, local_path)
    m.download_url(genes_file, dest_path=local_dir)
    
    logging.info("Downloading metadata file...")

    local_path = os.path.join(script_dir, 'cytobench-datasets', dataset + '-metadata.csv')
    # download_file(metadata_file, local_path)
    m.download_url(metadata_file, dest_path=local_dir)
    
    logging.info("Downloading counts file...")

    local_path = os.path.join(script_dir, 'cytobench-datasets', dataset + '-counts.mtx')
    # download_file(counts_file, local_path)
    m.download_url(counts_file, dest_path=local_dir)

    logging.info("Download complete.")

    return counts, genes, metadata