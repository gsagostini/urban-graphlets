#--------------------------------------------------------------------------------------------
# GOAL: given a node GeoDataFrame with the graphlet degree vectors, retrieve:
#          i. Distance matrix between all nodes
#         ii. Linkage matrix for hierarchical clustering of the nodes
#--------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

from src.utils import load_file
from src import node_clustering

#--------------------------------------------------------------------------------------------

_GDMs_dict_path = '../data/d2_processed/GDMs_dict.pickle'
_clustering_methods = ['single', 'complete', 'average', 'weighted']

#--------------------------------------------------------------------------------------------

def main(GDMs_dict_path, clustering_methods):
    #Load the GDMs dicitonary:
    GDMs_dict = load_file(GDMs_dict_path)
    #Get the distance matrix dictionary:
    Dmatrix_dict = node_clustering.get_D_matrix_dict(GDMS_dict)
    #Get the linkage matrix dictionary for each of the methods:
    for method in clustering_methods:
        linkage_dict = node_clustering.get_linkage_dict(Dmatrix_dict, method, save=True)
    
    return Dmatrix_dict, linkage_dict

if __name__ == '__main__':
    Dmatrix_dict, linkage_dict = main(_GDMs_dict_path, _clustering_methods)