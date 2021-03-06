#--------------------------------------------------------------------------------------------
# GOAL: cluster the nodes according to their Graphlet Degree Vectors (GDVs)
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
sys.path.append('../')

import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed

import multiprocessing
num_cores = multiprocessing.cpu_count()

from scipy.spatial.distance import minkowski
from scipy.spatial.distance import squareform
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage

#--------------------------------------------------------------------------------------------

def get_o(i):
    """
    Gets the number of orbits that influence orbit i
    
    :param i: int from 0 to 14 (orbit number)
    
    :return int
    """
    if i == 0:
        o = 1
    elif i in [1, 2]:
        o = 2
    elif i in [4, 6, 7]:
        o = 3
    elif i in [3, 5]:
        o = 4
    elif i == 9:
        o = 5
    elif i in [8, 10]:
        o = 6
    elif i == 11:
        o = 7
    elif i == 12:
        o = 11
    elif i == 13:
        o = 12
    elif i == 14:
        o = 15
    else:
        print('undefined')
        o = None
    return o

def get_w_vec(num_orbits=15, norm=True):
    """
    Gets the weight vector in the weighted Graphlet Degree distance
    
    :param num_orbits: int, default is 15 (graphlets up to size 4, including)
    :param norm: Bool, defaut is True, whether to normalize the weights (1-norm)
    
    :return np.array of shape (num_orbits,)
    """
    w = np.zeros(num_orbits)
    
    for i in range(num_orbits):
        w[i] = 1 - np.log(get_o(i))/np.log(num_orbits)
    
    if norm:
        w = w/np.linalg.norm(w, ord=1)
    
    return w

def get_GDVdistance(u_gdv, v_gdv, w):
    """
    Gets the weighted distance between two graphlet degree vectors
    
    :param u_gdv, v_gdv: np.arrays, the two GDVs
    :param w: np.array, the weight vector
    
    :return float
    """

    den = np.log(np.maximum(u_gdv, v_gdv)+2)
    u_tilde = np.log(u_gdv+1)/den
    v_tilde = np.log(v_gdv+1)/den
    return minkowski(u_tilde, v_tilde, p=1, w=w)


def get_D_matrix(GDM):
    """
    Gets the distance matrix between array of Graphlet Degree Vectors
    
    :param GDM: np.array where each row is a GDV i.e. corresponds to a node
    
    :return condensed distance matrix
    """
    
    w = get_w_vec(num_orbits=GDM.shape[1])
    return squareform(pairwise_distances(GDM, metric=get_GDVdistance, w=w, n_jobs=-1))

def get_D_matrix_dict(GDM_dict, save=True, test=False, filepath=None, num_cores=num_cores):
    """
    Gets a dictionary with the distance matrix corresponding to each GDM
    
    :param GDM_dict: dictionary, keys are tuples (city, country) and values are np.arrays
    
    :return dictionary with the same keys, values are condensed distance matrices
    """
    
    keys = list(GDM_dict.keys())
    inputs = list(GDM_dict.values())
    outputs = Parallel(n_jobs=num_cores)(delayed(get_D_matrix)(i) for i in inputs)
        
    D_dict = dict(zip(keys, outputs))
        
    if save:
        if filepath is None:
            if test:
                filepath = '../data/test-run/Dmatrix_dict.pickle'
            else:
                filepath = '../data/d3_results/Dmatrix_dict.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(D_dict, file)
        
    return D_dict

def get_linkage_dict(D_matrix_dict, cluster_method, save=True, test=False, filepath=None, num_cores=num_cores):
    """
    Gets a dictionary with the linkage matrix corresponding to each city
    
    :param D_matrix_dict: dictionary, keys are tuples (city, country) and values are condensed distance matrices
    :param cluster_method: string detailing type of agglomerative clustering; one of single, complete, average, or weighted
    
    :return dictionary with the same keys, values are linkage arrays
    """
    
    keys = list(D_matrix_dict.keys())
    inputs = list(D_matrix_dict.values())
    outputs = Parallel(n_jobs=num_cores)(delayed(linkage)(i, method=cluster_method, metric=None) for i in inputs)
        
    linkage_dict = dict(zip(keys, outputs))
        
    if save:
        if filepath is None:
            if test:
                filepath = '../data/test-run/linkage_dict' + cluster_method + '.pickle'
            else:
                filepath = '../data/d3_results/linkage_dict' + cluster_method + '.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(linkage_dict, file)
            
    return linkage_dict

def get_Dmatrix_and_linkages(GDM, cluster_methods, save=True, test=False, filepath=None, num_cores=num_cores):
    """
    Gets a distance matrix and a linkage matrix given a single GDM and a cluster method
    
    :param GDM: numpy array, graphlet degree matrix
    :param cluster_method: string detailing type of agglomerative clustering; one of single, complete, average, or weighted
    
    :return tuple of condensed distance matrix, array
    """
    
    if GDM is None:
        D_matrix = None
        linkage_arr_list = [None for i in cluster_methods]
    
    else:
        D_matrix = get_D_matrix(GDM)
        linkage_arr_list = Parallel(n_jobs=num_cores)(delayed(linkage)(D_matrix, method=cluster_method, metric=None)
                                                                      for cluster_method in cluster_methods)
    return (D_matrix, linkage_arr_list)
        

#--------------------------------------------------------------------------------------------