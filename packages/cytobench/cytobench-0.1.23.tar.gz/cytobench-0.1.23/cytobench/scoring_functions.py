import logging

import numpy as np

import scipy.stats
import sklearn.neighbors


class CoverageEstimator:
    
    '''
    The coverage estimator is the most important piece of the scoring pipeline
    It's initialized at every scoring round, and takes as input a set of reference points that
    will then be used to check how the simulated data is moving through the known manifold of any
    given dataset in a robust and biologically meaningful manner
    '''
    
    def __init__(self, reference_points):
        
        '''
        Initializes the nearest neighbors classifier, and the maximum achievable entropy score,
        which will then be used to normalize scores in the interval 0-1
        '''
        
        # used to bin counts
        self.n_reference_points = len(reference_points)
        
        # initiate reference ideal distribution for entropy comparison
        self.reference_entropy = scipy.stats.entropy(np.ones(self.n_reference_points))

        # create a NearestNeighbors classifier from the points
        self.model = sklearn.neighbors.NearestNeighbors(
            n_neighbors=1, n_jobs=-1, metric='cosine').fit(reference_points)
        
    def bin_observations(self, sample_population):
        
        '''
        Given a sample population, compute its distribution in the manifold using the class reference points
        to bin the samples in a multinomial-like manner, but using entropy instead for robustness purposes
        '''
        
        # convert a sample population to a distribution of neighbours
        _, indices = self.model.kneighbors(sample_population)

        # return the bincount wrt the reference points
        return np.bincount(indices[:,0], minlength=self.n_reference_points).astype(float)
    
    def entropy_test(self, sample_population, invalid_points = 0, validity_penalty = True):
        
        '''
        Given a sample population, compute its entropy score wrt the reference points and returnes the normalized value
        '''
        
        # return 0 for edge case where valid population is 0
        if len(sample_population) == 0:
            return 0
        
        # bin the sampled population
        observed_counts = self.bin_observations(sample_population)
        
        # penalize the invalid points either considering a fraction of the full score score
        # or by adding the invalid ones to the valid bin of maximum numerosity (thus penalizing entropy directly)
        if validity_penalty:
            
            # penalize reducing the score by the % of invalid points 
            valid_fraction = len(sample_population) / (len(sample_population) + invalid_points)
            
            entropy_score = scipy.stats.entropy(observed_counts) * valid_fraction
        
        else:
            
            # score purely on entropy, adding invalid points count to max bin
            # (less penalizing, works only if discriminator is biased toward rejection)
            observed_counts[np.argmax(observed_counts)] += invalid_points
            
            entropy_score = scipy.stats.entropy(observed_counts)
            
        # return normalized entropy score
        return entropy_score / self.reference_entropy
        
        
def interpolate_empty(v):
    
    '''
    Given a list of values with some elements == None, picks up the values before and after, and interpolates the 
    intermediate None values returning the numpy array with all elements filled; used in the approx scoring pipeline
    to save scoring epochs
    '''
    
    # make sure v is np array; None values will be cast to np.nan
    v = np.array(v, dtype=float)

    # collect np.nan indices
    nans = np.isnan(v)

    # indices for interpolation
    indices = np.arange(len(v))

    # interpolate using np.interp for indices where v is nan
    v[nans] = np.interp(indices[nans], indices[~nans], v[~nans])

    return v


def get_non_nan_extremes(v, i):
    
    '''
    Given a list of values with some elements == None, finds and returns the indices of the closest non nans value to its left and right
    (eventually returning itself if i==0 for the left value)
    Note: the algorithm is based on the assumption that i is not None and won't yield correct results otherwise
    '''
    
    # make sure v is np array; None values will be cast to np.nan
    v = np.array(v, dtype=float)

    # collect np.nan indices
    nans = np.isnan(v)

    # indices for interpolation
    indices = np.arange(len(v))
    
    # left index
    left_indices = indices[:i+1][~nans[:i+1]]
    ia = left_indices[-2:][0]
    
    # right index
    right_indices = indices[i:][~nans[i:]]
    ib = right_indices[:2][-1]

    return ia, ib


def score_sample(sample, data_validator, coverage_estimator):
    
    '''
    Given an array of samples, a data validator and coverage estimator, runs a scoring iteration wrt the given sample
    '''

    # validate sample
    validity_mask = data_validator.predict(sample).astype(bool)

    # score valid samples, adding penalty for the invalid ones
    sample_score = coverage_estimator.entropy_test(sample[validity_mask], invalid_points = sum(~validity_mask))

    # return the sample score and % of valid points at current iteration
    return sample_score, sum(validity_mask) / len(validity_mask)


def scoring_pipeline(
    sampling_fn, data_validator, coverage_estimator, current_population, max_iterations, 
    plateau_after_n, min_iterations, score_every_n, approx_scoring):
    
    '''
    Fully score a single trajectory (n of these will make up the actual score interval for a model)
    If approx_scoring = True we only score once every plateau_after_n epochs, then we go back and try to find the
    max score scoring intermediate points; if approx_scoring = True it is recommended to have plateau_after_n set 
    to a base 2 exponent in order to take full advantage of the scoring process
    '''
    
    # initiate cycle variables
    max_score, plateau_epoch, population_size = 0, 0, len(current_population)

    # initialize stats 
    valid_points, scores, populations = [], [], [np.copy(current_population)]
    
    # scoring step is determined by approx scoring
    scoring_step = plateau_after_n if approx_scoring else score_every_n

    # start sampling
    for n_iteration in range(max_iterations):

        # actually score the model only once every score_every_n epochs,
        # while keeping on sampling at every iteration
        # note: the first iteration should and will always be scored for the baseline
        if n_iteration % scoring_step == 0:
            
            sample_score, sample_validity = score_sample(current_population, data_validator, coverage_estimator)
            
            # store stats
            scores.append(sample_score)
            valid_points.append(sample_validity)

            # check for new high
            if sample_score > max_score:
                max_score = sample_score
                plateau_epoch = n_iteration

            # interrupt in case of plateau (if min_epochs has been reached)
            # using > plateau_after_n (rather than >=) will ensure that we extend for one extra cycle, which is needed for the part that comes after
            if n_iteration - plateau_epoch > plateau_after_n and n_iteration >= min_iterations:
                break
                
            # remove sampled populations that for sure we won't score to free up memory for long runs
            # the populations to keep are the ones within plateau_after_n radius of plateau_epoch and
            # from the endcap, since a new max might be coming; we do this but simply iterating over the
            # whole array to keep the code clean
            if approx_scoring:
                for i in range(len(populations)):
                    if populations[i] is not None:
                        if np.abs(i - plateau_epoch) > plateau_after_n and np.abs(i - n_iteration) > plateau_after_n:
                            populations[i] = None
            
        else:
            valid_points.append(None)
            scores.append(None)
        
        # sample new population
        current_population = sampling_fn(current_population)
        populations.append(np.copy(current_population) if approx_scoring else None)

        # check that the function didn't drop any point
        assert len(current_population) == population_size, "Sampling function seems to have dropped some points"
        
        # note: the max value of reads should be << 100, if it goes over 1000 the sampling has become unstable and will likely crash the scoring
        if np.any(current_population > 1000):
            logging.warning(f'Sampled values are diverging: max = {np.max(current_population)}, note that the maximum count value should be << 100')
            break
        
    # check the indices of the first not None value before and after plateau_epoch
    ia, ib = get_non_nan_extremes(scores, plateau_epoch)
        
    # compute scores of intermediate values until the desired granularity has been reached
    while max(plateau_epoch - ia, ib - plateau_epoch) > score_every_n:
        
        # consider intermediate point between last not None and plateau_epoch from left and right
        ia = np.ceil((plateau_epoch + ia) / 2).astype(int)
        ib = np.floor((plateau_epoch + ib) / 2).astype(int)
        
        for i in [ia, ib]:

            if scores[i] is None:
                
                sample_score, sample_validity = score_sample(populations[i], data_validator, coverage_estimator)

                # store stats
                scores[i] = sample_score
                valid_points[i] = sample_validity

                # check for new high
                if sample_score > max_score:
                    max_score = sample_score
                    plateau_epoch = i
                    
        # update the empty indices and iterate
        ia, ib = get_non_nan_extremes(scores, plateau_epoch)
        
    # return the final validities and scores, interpolating the values that have not been scored
    return interpolate_empty(valid_points), interpolate_empty(scores)


def score_model(
    sampling_fn, data_validator, environment_points, expand_n = 100, n_trajectories = 100, max_iterations = 500, plateau_after_n = 16, 
    min_iterations = 0, score_from_zero = True, score_every_n = 1, approx_scoring = True):
    
    ''' 
    Run full scoring pipeline for a trajectory
    '''
    
    assert len(environment_points) >= expand_n * n_trajectories, 'insufficient number of points compared to replicates'
    assert score_every_n >= 1

    # select random subset of points to be used as reference for manifold exploration
    points_subset = np.random.choice(len(environment_points), size = expand_n * n_trajectories, replace=False)
    
    # initialize coverage estimator
    coverage_estimator = CoverageEstimator(np.copy(environment_points[points_subset]))

    # sample initial population for expansion
    points_subset = np.random.choice(len(environment_points), size = expand_n, replace=False)
    initial_points = np.copy(environment_points[points_subset])

    # consider n_trajectories copies for each point
    current_population = np.repeat(initial_points, repeats=n_trajectories, axis=0)
    
    # run scoring pipeline
    valid_points, scores = scoring_pipeline(
        sampling_fn, data_validator, coverage_estimator, current_population, 
        max_iterations, plateau_after_n, min_iterations, score_every_n, approx_scoring
    )

    # eventually set min score to zero (in which case make sure we don't get into negative values for lower scores)
    if score_from_zero:
        scores = np.maximum(0, (np.array(scores) - scores[0]) / (1-scores[0]))
        
    # return score in % and valid points progression
    return np.array(scores) * 100, valid_points