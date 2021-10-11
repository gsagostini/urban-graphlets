#--------------------------------------------------------------------------------------------
# GOAL: obtain the Graphlet Degree Matrices (GDMs) of each city
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
from tqdm import tqdm
sys.path.append('../')

import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox

from src.vars import ghsl_crs
from src.orcalib import orca

test=False

#--------------------------------------------------------------------------------------------

def get_node_geodataframe(graph, GDM, proj=ghsl_crs):
    """
    Get GeoDataFrame with the nodes of the street networks (represented as points) and
      their respective Graphlet Degree Vectors (GDVs)
    
    :param graph: simplified street network whose nodes are indexed sequentially as integers
    :param GDM: Graphlet Degree Matrix (GDM), rows correspond to nodes via index
    :param proj: crs to project the gdf (using the default GHSL throughout the project, Mollweide)
    
    return: GeoDataFrame, geometries are points (nodes) and GDVs are arrays of integers
    """    
    nodes_gdf = ox.graph_to_gdfs(graph, edges=False).to_crs(proj)
    nodes_gdf['GDV'] = pd.Series(GDM)
    
    return nodes_gdf


def get_GDMs(graphs_dict, graphlets_up_to=4, test=test, save=True, filepath=None, get_nodes_gdf=False, proj=ghsl_crs):
    """
    Get Graphlet Degree Matrices (GDM) for each graph in the dictionary.
    
    :param graphs_dict: dictionary with simplified street networks, keys are tuples (city, country)
    :param graphlets_up_to: 4 or 5, maximum size of graphlets whose orbits we want to compute
    :param test: Boolean, whether this is the test run
    :param save: Boolean, whether the graph dictionary should be saved
    :param filepath: string, if saved file must be named in a particular way, default is graphs_dict.pickle
    :param get_nodes_gdf: Boolean, whether to also obtain the nodes GeoDataFrame simultaneously
    :param proj: crs to project the gdf (using the default GHSL throughout the project, Mollweide)
    
    return: dictionary with GDMs, keys are tuples (city, country)
            and if get_nodes_gdf = True, also dictionary with nodes GeoDataFrames, keys are tuples (city, country)
    """
    GDMs_dict = dict()
    
    if get_nodes_gdf:
        node_gdfs_dict = dict()
    
    for city, country in tqdm(graphs_dict.keys()):
        
        graph = graphs_dict[(city, country)]
        
        if graph is None:
            GDMs_dict[(city, country)]  = None

            if get_nodes_gdf:
                node_gdfs_dict[(city, country)] = None            
            
        else:
            GDM = orca.orbit_counts('node', graphlets_up_to, graph)
            GDMs_dict[(city, country)] = np.array(GDM)

            if get_nodes_gdf:
                node_gdf = get_node_geodataframe(graph, GDM, proj)
                node_gdfs_dict[(city, country)] = node_gdf
               
    if save:
        if filepath is None:
            if test:
                filepath = '../data/test-run/GDMs_dict.pickle'
            else:
                filepath = '../data/d2_processed/GDMs_dict.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(GDMs_dict, file)
            
        if get_nodes_gdf:
            if save:
                if test:
                    filepath = '../data/test-run/node_gdfs_dict.pickle'
                else:
                    filepath = '../data/d2_processed/node_gdfs_dict.pickle'

                with open(filepath, 'wb') as file:
                    pkl.dump(node_gdfs_dict, file)
    
    if get_nodes_gdf:
        return GDMs_dict, node_gdfs_dict
    else:
        return GDMs_dict

def get_node_geodataframes(graphs_dict, GDMs_dict, proj=ghsl_crs, test=test, save=True, filepath=None):
    """
    Get GeoDataFrames with the nodes of all street newtworks (represented as points) and
      their respective Graphlet Degree Vectors (GDVs)
    
    :param graphs_dict: dictionary with simplified street networks, keys are tuples (city, country)
    :param GDMs_dict: dictionary with Graphlet Degree Matrices (GDMs), keys are tuples (city, country)
    :param proj: crs to project the gdf (using the default GHSL throughout the project, Mollweide)
    :param test: Boolean, whether this is the test run
    :param save: Boolean, whether the graph dictionary should be saved
    :param filepath: string, if saved file must be named in a particular way, default is graphs_dict.pickle
    
    return: dictionary with GeoDataFrames, keys are tuples (city, country)
    """
    node_gdfs_dict = dict()
    
    for city, country in graphs_dict.keys():
        
        graph = graphs_dict[(city, country)]
        GDM = GDMs_dict[(city, country)]
        
        node_gdf = get_node_geodataframe(graph, GDM, proj)
        node_gdfs_dict[(city, country)] = node_gdf
    
    if save:
        if filepath is None:
            if test:
                filepath = '../data/test-run/node_gdfs_dict.pickle'
            else:
                filepath = '../data/d2_processed/node_gdfs_dict.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(node_gdfs_dict, file)
    
    return node_gdfs_dict

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':
    pass