#--------------------------------------------------------------------------------------------
# GOAL: given a list of cities, retrieve their
#          i. Administrative boundaries (shapely.Polygon)
#         ii. Pre-processed street network (NetworkX.Graph)
#        iii. Street intersection graphlet degree vectors (GeoPandas.GeoDataFrame)
#--------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

from src import get_cities
from src import get_boundary
from src import get_graph
from src import get_GDM

#--------------------------------------------------------------------------------------------

_list_cities_path = '../data/d1_raw/node_list_of_cities.csv'

#--------------------------------------------------------------------------------------------

def main(list_cities_path):
    #Get the list of cities and countries:
    all_cities, all_countries = get_cities.get_cities_and_countries(method='csv', test=False, cities_filepath=list_cities_path)
    #Get the administrative boundaries, save them as a dictionary:
    boundaries_dict = get_boundary.get_boundaries(cities=all_cities, countries=all_countries, method='osmnx', test=False, save=True)
    #Get the street networks, save them as a dictionary:
    graphs_dict = get_graph.get_graphs(boundaries_dict, test=False, save=True)
    #Get the Graphlet Degree Matrices and the corresponding GeoDataFrames, save tehm as a dictonary
    GDMs_dict, nodes_gdfs_dict = get_GDM.get_GDMs(graphs_dict, test=False, get_nodes_gdf=True, save=True)
    
    return boundaries_dict, graphs_dict, GDMs_dict, nodes_gdfs_dict

if __name__ == '__main__':
    boundaries_dict, graphs_dict, GDMs_dict, nodes_gdfs_dict = main(_list_cities_path)