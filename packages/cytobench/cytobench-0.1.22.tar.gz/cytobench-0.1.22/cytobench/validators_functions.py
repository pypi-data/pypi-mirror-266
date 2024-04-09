import os
import joblib

import logging

import numpy as np
import pandas as pd

import sklearn.pipeline
import sklearn.decomposition
import sklearn.mixture

from .datasets_manager import get_dataset_path, load_dataset

class Validator:
    
    '''
    Builds a data distribution validator using PCA for dimensionality reduction and GMM for density estimate
    Note: the model is quite relaxed, but at the same time fairly unbiased and good enough to capture points
    that are significantly far from the original data distribution without having to impose almost any assumption
    on the underlying data (which works well given our range of datasets)
    '''
    
    def __init__(self, pca_components=None, gm_components=None, gm_covariance='diag', gm_init='k-means++'):
        
        self.pca_components = pca_components
        self.gm_components = gm_components
        self.gm_covariance = gm_covariance
        self.gm_init = gm_init
        
        self.model = None
        self.threshold_quantile = None
    
    def fit(self, X, X_val = None):
        
        '''
        Fits a PCA and GMM using an approx number of clusters and PCA components 
        '''
        
        # if pca_components = None, infer using default pipeline
        if self.gm_components is None:
            self.gm_components = len(X) // 200
        
        # if gm_components = None, infer using 1 component every 200 samples
        if self.pca_components is None:
            self.pca_components = self.infer_pca_components(X)
        
        # model pipeline
        self.model = sklearn.pipeline.Pipeline(steps=[
            ('pca', sklearn.decomposition.PCA(n_components=self.pca_components)),
            ('gmm', sklearn.mixture.GaussianMixture(n_components=self.gm_components, covariance_type=self.gm_covariance, init_params=self.gm_init))
        ])
        
        logging.info('Fitting GMM')
        
        # fit GMM
        self.model.fit(X)
        
        # after fitting the GMM we actually set a manual threshold for valid points, by default such 1/20 point will be considered outliers
        # note: in general this is already a quite generous model considering the underlying data, and having it more accepting than this
        # will result in a minimal discriminative power (but can be set so by the user for testing)
        logging.info('Calibrating threshold')
        
        # calibrate validity threshold on validation set
        if X_val is None:
            X_val = X
            
        return self.calibrate_threshold(X_val)
        
    def infer_pca_components(self, X, max_components = 100, min_increase = 1.01):
        
        '''
        The number of PCA components for the dimensionality reduction is inferred by considering the first n dimensions where
        each one contributes at least 1% to the cumulative explained variance
        '''
        
        logging.info('Inferring PCA components for GMM')
        
        # train a PCA model
        pca = sklearn.decomposition.PCA(n_components=max_components)
        pca.fit(X)

        # compute explained variance progression for the given dataset
        explained_variances = np.cumsum(pca.explained_variance_ratio_)
        
        # yield the last dimension where the increase of explained variance was at least min_increase
        return np.where(explained_variances[1:] / explained_variances[:-1] >= min_increase)[0][-1] + 1
    
    def calibrate_threshold(self, X, calibration_quantile = .05):
        
        '''
        Set reference score threshold for valid/invalid points
        '''
        
        self.threshold_quantile = np.quantile(self.model.score_samples(X), calibration_quantile)
        
    def predict(self, X):
        
        '''
        Predict validity True/False
        '''
        
        # automatically invalidate any negative count
        pred = ~ np.any( (X < 0), axis=1 )
        
        # score potentially valid samples
        pred[pred == True] = self.model.score_samples(X[pred == True]) > self.threshold_quantile
        
        # return complete validity prediction
        return pred


def generate_negative_samples(X, generate_n):
    
    '''
    Generate negative samples by interpolating real ones in the original space
    Used as indicative metric of how well the model rejects synthetic samples; note that datasets with different 
    intrinsic densities will vary greatly in this regard, but it can still be used as a coarse reference 
    Note that using these samples to train a energy-based model will result in an extremely biased and weak discriminator
    '''
    
    # shift to avoid duplicates
    max_n = (len(X) // 2 - 2)
    
    # sample two columns max_n, then one *2 and the other *2+1
    cells_i = np.random.randint(max_n, size=(generate_n,2)) * 2
    cells_i[:,1] += 1
    
    # select array of float 0-1
    positions = np.random.rand(generate_n, 1)
    
    # capture intermediate point
    samples = X[cells_i[:,0]] * positions + X[cells_i[:,1]] * (1-positions)
    
    # return training points
    return samples


def score_validator(model, X_test):
    
    '''
    Compute and return true positives and negatives detection rate
    '''
    
    positives = sum(model.predict(X_test)) / len(X_test)
    negatives = sum(~model.predict(generate_negative_samples(X_test, len(X_test)))) / len(X_test)
    
    return [positives, negatives, np.mean([positives, negatives])]


def get_training_masks(n_samples, train_p = .6, validation_p = .3, test_p = .1):
    
    '''
    Given a sample numerosity, generate training, validation and test masks
    '''
    
    assert np.allclose(train_p + validation_p + test_p, 1), "masks don't add up to 1"

    # sample train test validation datasets in order to have them fixed through the project
    training_mask, validation_mask, test_mask = np.full(n_samples, False), np.full(n_samples, False), np.full(n_samples, False)

    training_mask[ np.random.choice(n_samples, int(n_samples*train_p), replace=False) ] = True
    validation_mask[ np.random.choice(np.arange(n_samples)[~training_mask], int(n_samples*validation_p), replace=False) ] = True
    test_mask[ np.arange(n_samples)[~training_mask & ~validation_mask] ] = True
    
    # double check
    assert sum(training_mask) + sum(validation_mask) + sum(test_mask) == n_samples, "masks don't correspond to input numerosity"

    # return masks
    return training_mask, validation_mask, test_mask


def train_and_score_validator(dataset, split_i, internal_data):
    
    '''
    Given a dataset specification, loads it, trains the distribution validator and stores it in the same folder
    '''
    
    X, genes, metadata = load_dataset(dataset, split_i, internal_data)

    training_mask, validation_mask, test_mask = get_training_masks(len(X))

    logging.info(f'\nTraining validator for "{dataset}" dataset, split {split_i+1}, {"internal" if internal_data else "external"} distribution')

    # train discriminator
    model = Validator()
    model.fit(X[training_mask], X[validation_mask])

    logging.info(f'Training completed\nScoring on test set...')

    # computes and returns consistency of acceptance/rejection rate on test set
    positive, negative, total = np.round(score_validator(model, X[test_mask]), 3)

    logging.info('Positives: {}\nNegative: {}\nTotal: {}'.format(positive, negative, total))

    model_path = os.path.join(get_dataset_path(dataset), 'validators', f'{split_i}-{internal_data}.joblib')

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # store the model
    return joblib.dump(model, model_path)

    
def train_validators(dataset):
    
    '''
    Train all data validators for a given dataset
    '''

    # train models for all splits
    for split_i in range(get_dataset_splits(dataset)):
        
        for internal_data in [True, False]:
            
            train_and_score_validator(dataset, split_i, internal_data)
            
    # training completed
    return logging.info('Training completed.')


def load_validator(dataset, split = 0, internal = True, train_missing_validators = True):
    
    '''
    Loads the data validator for a given dataset
    If it doesn't exist and train_missing_validators = True, then trains it on the fly before returning it
    '''
    
    validator_path = os.path.join(get_dataset_path(dataset), 'validators', f'{split}-{internal}.joblib')
    
    # train the validators with default parameters if they don't exist
    if not os.path.exists(validator_path) and train_missing_validators:
        
        logging.info('Data validator not found, training with default parameters...')
        
        train_and_score_validator(dataset, split, internal)
    
    assert os.path.exists(validator_path), f'Validator not found at {validator_path}; run load_validator({dataset}) to train validators for the first time'
    
    return joblib.load(validator_path)