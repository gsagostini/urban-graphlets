#--------------------------------------------------------------------------------------------
# GOAL: cluster the tiles according to their Graphlet Correlation Matrices
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
sys.path.append('../')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from collections import Counter

from scipy.spatial.distance import squareform
from scipy.spatial.distance import pdist
import scipy.cluster.hierarchy as shc

from src.utils import get_categorical_cmap
from src.vars import available_metrics

test=True

#--------------------------------------------------------------------------------------------

class HierClustering:
    """
    :attr data: GeoDataFrame
    :attr method: string, clustering method
    :attr metric: string, distance function
    :attr dmatrix_cond: condensed matrix, distance between GCMs
    :attr linkage: array, linkage from scipy.hierarchy
    :attr gdf_with_clusters: dict, keys are ints representing flat cluster assignments
    """
    
    def __init__(self, full_gdf, method='ward', metric='euclidean', optimal_ordering=False, vectorized=True):
        """
        :param full_gdf: GeoDataFrame of tiles containing classification, GCM, and valid_GCM columns
        :param method: string, clustering algorithm to use, for example:
            - 'ward'
            - 'single'
            - 'average'
            - 'complete'
        :param metric: string or callable, metric to impose in the space of GCMs
        :param vectorized: Boolean, if True treat GCMs as 55-dimensional vectors
        :param optimal_ordering: Boolean, see scipy documentation
        """
        
        #Initialize parameters
        self.data = full_gdf
        self.method = method
        self.metric = metric
        
        #If vectorized metrics are used, we need the condensed distance matric of the array of 55-dimensional GCM vectors:
        if vectorized:
            self.dmatrix_cond = pdist(self.get_GCM_vectorized(), metric=metric)
        #If we are not vectorizing the matrices, we need to pass the metric to compute the pairwise dist. matrix (see scipy):    
        else:
            self.dmatrix_cond = pdist(self.data['GCM'].dropna().values, metric=metric)
            
        #Use the condensed distance matrix to obtain the linkage:
        self.linkage = shc.linkage(self.dmatrix_cond, method=method, metric=None, optimal_ordering=optimal_ordering)
        
        #Dictionary where full gdfs for cluster assignments will be stored, keys are the number of clusters:
        self.gdf_with_clusters_dict = dict()
        
    def get_GCM_vectorized(self, n_orbits=11):
        """
        Gets the non-redundant vectors representing each GCM
        
        return array with n observations and n_orbits choose 2 elements per vector (default is 55)
        """
        
        tri_indices = np.triu_indices(n_orbits, k=1)
        GCM_full_vectors = np.stack(self.data['GCM'].apply(lambda x: x[tri_indices]).values)[self.data['valid_GCM']]

        return GCM_full_vectors
    
    def save_gdf_with_clusters(self, gdf_file, file_id='', test=test):
        """
        Saves the gdf with clusters
        
        :param gdf_file: GeoDataFrame with clusters, to be saved
        :param file_id: string, identification for the filename
        :param test: Boolean, wehther this is the test run
        """
        #Construct the filename:
        filename = 'gdf_hiercluster_' + self.metric + '_' + self.method + '_' + file_id
        
        #Find the full filepath:
        if test:
            filepath = '../data/test-run/' + filename + '.pickle'
        else:
            filepath = '../data/d3_results/' + filename + '.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(gdf_file, file)

    def add_cluster_column(self, flat_cluster_arr):
        """
        Gets GeodataFrame with 'cluster' columnm where elements correspond to cluster of a tile, including those with cluster None
        
        :param flat_cluster_arr: np.array of ints, cluster corresponding to valid tile
        
        return: GeoDataFrame
        """
        
        cluster_columns = self.data['valid_GCM'].replace({True:flat_cluster_arr, False:None}).astype('Int64')
        full_gdf_with_clusters = self.data.assign(cluster=cluster_columns)
        
        return full_gdf_with_clusters
    
    def relabel_clusters(self, cluster_arr):
        """
        Relabels clsuters so that cluster labels decrease according to cluster sizes
         i.e. 0 is the largest cluster, 1 is the second largest, etc.
         
        :param cluster_arr: np.array of cluster assignments
        
        return re-ordered cluster assignment
        """
        counts = Counter(cluster_arr)
        
        ordered_cluster_arr = cluster_arr
        
        return ordered_cluster_arr
    
    def get_flat_clusters(self, threshold, method='maxclust', save=True, test=test, ordered=True):
        """
        Gets the flat cluster assignment given the threshold
        
        :param method: string (see scipy doc.), method to cut linkage. Default is max number of clusters
        :param threshold: float, depends on method. Default is int for max number of clusters
        :param ordered: Boolean, if True then cluster labels decrease according to cluster sizes
        
        return: np.array of flat cluster assignments (including None)
        
        OBS: if the method provides involves thresholding by the number of clusters, add gdf to dictionary.
        """
        
        #Use scipy to get the flat clusters, and then add the column to the data GDF
        flat_cluster_arr = shc.fcluster(self.linkage, t=threshold, criterion=method)
        if ordered:
            flat_cluster_arr = self.relabel_clusters(flat_cluster_arr)
        
        full_gdf_with_clusters = self.add_cluster_column(flat_cluster_arr)
        
        #If thresholidng by number of clusters, update the dicitonary:
        if 'maxclust' in method:
            self.gdf_with_clusters_dict[threshold] = full_gdf_with_clusters
        
        #Save the file:
        if save:
            self.save_gdf_with_clusters(full_gdf_with_clusters, file_id=str(threshold), test=test)
        
        return flat_cluster_arr
    
    def plot_dendrogram(self, order='descending',
                        set_colors=False, color_threshold=0,
                        truncate_mode='level', p=7,
                        ax=None, title='Hierarchical Cluster', description=True,
                        return_dend=False):
        """
        Displays the dendrogram correponding to a linkage matrix (i.e. given method and metric)
        
        :param set_colors: Boolean, determine whether we care about the colors or monochromatic
        :param color_threshold: None or float, color_threshold
        :param order: False, 'ascending' or 'descending', how to order the nodes by count
        :param ax: Ax to plot dendogram
        :param title: string, plot main title
        :param description: Boolean, whether to add method and metric to title
        
        return ax, if return_dend return ax, dendrogram_dict
        """
        #If no ax was given, get one:
        if ax is None:
            fig, ax = plt.subplots(figsize=(20,15))
        
        if set_colors:
            print("Not implemented yet")
            #Get the color pallete:
            cmap_dict = get_categorical_cmap(self.gdf_with_clusters_dict[5])
            cmap_list = [cmap_dict[cluster] for cluster in sorted(cmap_dict.keys())]
            shc.set_link_color_palette(cmap_list)
        else:
            shc.set_link_color_palette(['C0'])
        
        #Call the dendrogram function with the required arguments:
        dend = shc.dendrogram(self.linkage, count_sort=order, color_threshold=None,
                              truncate_mode=truncate_mode, p=p,
                              ax=ax)
        
        #Add the title:
        if description:
            title = title + ' ('+self.method+')'
        plt.title(title, size=20)
        
        plt.show()
        
        #Return depends on parameters:
        if return_dend:
            return ax, dend
        else:
            return ax
    
    def plot_city(self, city, n_clusters, ax=None, method='maxclust', title=None):
        """
        Displays the map of a city with the colored tiles according to a flat clustering assignment
        
        :param city: string, city to plot
        :param n_clusters: int, number of clusters to identify flattened assignment
        
        return ax
        """
        #Standard version of flat clusters involves n_clusters:
        if 'maxclust' in method:
            #Locate the gdf with the assignment if possible:
            if n_clusters in self.gdf_with_clusters_dict.keys():
                gdf_with_clusters = self.gdf_with_clusters_dict[n_clusters]
            else:
                gdf_with_clusters = self.get_flat_clusters(n_clusters)
                
        #If we used another criterion, we need to compute the assignment
        else:
            gdf_with_clusters = self.get_flat_clusters(n_clusters, method)

        #Truncate the gdf for the city portion:
        city_gdf_with_clusters = gdf_with_clusters[gdf_with_clusters['city'] == city]
        
        #Get the colors:
        colors_dict = get_categorical_cmap(gdf_with_clusters, 'cluster')
        
        #Get axis if not passed:
        if ax is None:
            fig, ax = plt.subplots(figsize=(20,20))
        
        #Plotting routine using the colors provided:
        city_gdf_with_clusters.plot(ax=ax, categorical=True,
                                    color=city_gdf_with_clusters['cluster'].map(colors_dict),
                                    missing_kwds={'color': 'lightgrey', 'label':'undefined', 'hatch':'///'})
        
        #Adjust plot:
        if title is None:
            title=city
        ax.set_title(title, fontsize=50)
        ax.set_axis_off()
        
        return ax