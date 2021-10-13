#--------------------------------------------------------------------------------------------
# GOAL: given a node GeoDataFrame with the graphlet degree vectors, retrieve:
#          i. Distance matrix between all nodes
#         ii. Linkage matrix for hierarchical clustering of the nodes
#--------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

from src.utils import load_file, save_file
from src import node_clustering

from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()

#--------------------------------------------------------------------------------------------

_GDMs_dict_path = '../data/d2_processed/GDMs_dict.pickle'
_clustering_methods = ['single', 'complete', 'average', 'weighted']

#--------------------------------------------------------------------------------------------

def main(GDMs_dict_path, cluster_methods, num_cores=num_cores):
    #Load the GDMs dicitonary:
    GDMs_dict = load_file(GDMs_dict_path)
    keys = list(GDMs_dict.keys())
    GDMs = list(GDMs_dict.values())
    
    #Get the distance matrices and linkage matrices:
    outputs = Parallel(n_jobs=num_cores)(delayed(node_clustering.get_Dmatrix_and_linkages)(GDM, cluster_methods=cluster_methods)
                                                                                           for GDM in GDMs)
    #Save the distance matrix dictionary:
    D_matrix_list = [output_tuple[0] for output_tuple in outputs]
    D_matrix_dict = dict(zip(keys, D_matrix_list))
    f_path = '../data/d3_results/Dmatrix_dict.pickle'
    f = save_file(D_matrix_dict, f_path)
    
    #Save the linkage dictionaries (one per method):
    i = 0
    for method in cluster_methods:
        linkage_list = [output_tuple[1][i] for output_tuple in outputs]
        linkage_dict = dict(zip(keys, linkage_list))
        f_path = '../data/d3_results/' + method + '_linkage_dict.pickle'
        f = save_file(linkage_dict, f_path)
        i+=1
    
    return "Distance and linkage matrices saved"

if __name__ == '__main__':
    done = main(_GDMs_dict_path, _clustering_methods)