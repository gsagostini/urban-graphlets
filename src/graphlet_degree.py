#--------------------------------------------------------------------------------------------
# GOAL: visualize the graphlet degree distributions
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
sys.path.append('../')


import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
import numpy as np
from tqdm import tqdm

from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()

import matplotlib.pyplot as plt
import seaborn as sns

from src.orcalib import orca

#--------------------------------------------------------------------------------------------

def add_GDV(graph, graphlets_up_to=4):
    """
    Adds each of the graphlet orbit degrees as node attribtues to the graph
    
    :param graph: ox.Graph
    :param graphlets_up_to: int, maximum node size of graphlets to compute (either 4 or 5)
    
    return: ox.Graph, gpd.GeoDataFrame (nodes)
    """
    #Get the Graphlet Degree Matrix using OrCA:
    GDM = np.array(orca.orbit_counts('node', graphlets_up_to, graph))
    #Create the node and edge GeoDataFrames:
    node_gdf, edge_gdf = ox.utils_graph.graph_to_gdfs(graph)
    #Add the GDM to the node GeoDataFrame:
    for orbit in range(15):
        node_gdf[orbit] = GDM[:,orbit]
    #Rebuild the graph:
    new_graph = ox.utils_graph.graph_from_gdfs(node_gdf, edge_gdf)
    
    return new_graph, node_gdf

def prepare_gdf(original_gdf, n_orbits=15):
    """
    Breaks a GeoDataFrame with a GDV column into several columns whose name is the corresponding orbit
    
    :param original_gdf: GeoDataFrame with column GDV (lists)
    :param n_orbits: int, length of each GDV
    
    return: GeoDataFrame
    """
    GDV_df = pd.DataFrame(original_gdf["GDV"].to_list(), columns=[k for k in range(n_orbits)], index=original_gdf.index)
    new_gdf = original_gdf.merge(GDV_df, on='osmid').drop('GDV', axis=1)
    return new_gdf


def join_gdfs(gdfs, cities, prepared=False, n_orbits=15):
    """
    Joing a list of GeoDataFrames corresponding to cities
    
    :param gdfs: list of GeoDataFrames
    :param cities: list of city names
    
    return: GeoDataFrame
    """
    #First prepare the gdfs by blowing up the GDV columns:
    if not prepared:
        prepared_gdfs = []
        for gdf in gdfs:
            prepared_gdfs.append(prepare_gdf(gdf, n_orbits))    
    else:
        prepared_gdfs = gdfs
        
    #Add city columns:
    named_gdfs = []
    for gdf, city in zip(prepared_gdfs, cities):
        gdf['city'] = city
        named_gdfs.append(gdf)
    
    #Join the GeoDataFrames:
    joined_gdf = gpd.GeoDataFrame(pd.concat(named_gdfs, axis=0, ignore_index=True), crs = named_gdfs[0].crs)
    
    return joined_gdf

def plot_hist(data, orbit_no, cities=None, together=False):
    """
    Plot histogram for certain graphlet degree distribution
    
    :param data: DataFrame
    :param orbit_no: int, orbit to plot
    :param cities: list of city names, if None use all cities in dataframe
    :param together: Boolean, whether to plot histograms for all cities on the same plot or by row
    
    return: FacetGrid
    """
    if cities is not None:
        #Select the part of the dataframe that we want to evaluate:
        boolean_series = data.city.isin(cities)
        filtered_data = data[boolean_series]
    else:
        filtered_data = data  
    
    xmax= min(np.max(filtered_data[orbit_no].values), 40)
    
    #Plot
    if together or (cities is not None and len(cities)==1):     
        facet = sns.displot(data=filtered_data, x=orbit_no,
                            hue='city',
                            kind='hist', discrete=True, stat="percent", common_norm=False, fill=True, multiple='layer', element='bars',
                            height=10, aspect=2, facet_kws={'xlim':(0, xmax), 'sharex':True, 'sharey':True})
    else:
        facet = sns.displot(data=filtered_data, x=orbit_no,
                            row='city',
                            kind='hist', discrete=True, stat="percent", common_norm=False, fill=True, multiple='layer', element='bars',
                            height=10, aspect=2, facet_kws={'xlim':(0, xmax), 'sharex':True, 'sharey':True, 'margin_titles':False})
        facet.set_titles(row_template='{row_name}', size=30)
        facet.fig.tight_layout()
        
    facet.set_ylabels(label='Percentage', fontsize=20)
    facet.set_xlabels(label='Degree for orbit ' + str(orbit_no), fontsize=20)
        
    return facet

def plot_boxplot(data, orbit_no, outliers=False):
    fig, ax = plt.subplots(figsize=(5, 10))
    ax = sns.boxplot(data=data, y=orbit_no, x='city', ax=ax, showfliers=outliers)
    return ax

#DON'T USE
def deg_colors(node_gdf, orbit_no, target_deg):
    #If we have an integer, check whether the degree matches:
    if type(target_deg)==int:
        color_bool = node_gdf[orbit_no] == target_deg
    #Otherwise we passed a list:
    else:
        color_bool = node_gdf[orbit_no].isin(target_deg)
    
    #Convert Boolean series to colors
    color = color_bool.replace({True: 1, False: 0})
    
    return color

