#--------------------------------------------------------------------------------------------
# GOAL: obtain the boundaries (polygons) of each city
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
sys.path.append('../')

import networkx as nx
import osmnx as ox
import fiona
import geopandas as gpd
from tqdm import tqdm

from src.vars import ghsl_crs
from src.get_cities import get_processed_urbancentre_gdf

test=False

#--------------------------------------------------------------------------------------------

def get_boundaries_GHSL(ghsl_gdf=None):
    """
    Get boundaries (polygons) for all the cities provided using the GSHL data
    
    :param ghsl_gdf: GeoDataFrame, if None full gdf is computed
    
    return: dictionary with boundaries, keys are tuples (city, country)
    """
    
    #If no GHSL GDF was given, we must obtain it:
    if ghsl_gdf is None:
        ghsl_gdf = get_processed_urbancentre_gdf(sample=False)
        
    #Get the city and country lists:
    cities = list(ghsl_gdf['urban centre'])
    countries = list(ghsl_gdf['country'])
    
    #Boundaries are passed as a GeoDataFrame of a single row:
    boundaries = [ghsl_gdf.iloc[[i]].reset_index() for i in range(len(cities))]
    
    #Zip cities and countries to obtain keys and create the dictionary
    keys = list(zip(cities, countries))
    boundaries_dict = dict(zip(keys, boundaries))
    
    return boundaries_dict

def get_boundaries_osmnx(cities, countries, proj=ghsl_crs):
    """
    Get boundaries (polygons) for all the cities provided using the GHSL data
    
    :param cities: list of cities
    :param countries: list of countries
    :param proj: crs to project the boundary (using the default GHSL throughout the project, Mollweide)
    
    return: dictionary with boundaries, keys are tuples (city, country)
    """
    boundaries_dict = dict()
    
    for city, country in tqdm(zip(cities, countries), total=len(cities)):
        try:
            boundary = ox.geocode_to_gdf(city +', '+country)
            boundaries_dict[(city, country)] = boundary
        except:
            print("Problem with ", city +', '+country)
    
    return boundaries_dict

def get_boundaries(cities=None, countries=None, method='osmnx', proj=ghsl_crs, ghsl_gdf=None, test=test, save=True, filepath=None):
    """
    Get boundaries (polygons) for all the cities provided
    
    :param cities: list of cities (ignored in GHSL method)
    :param countries: list of countries (ignored in GHSL method)
    :param method: 'osmnx' or 'GHSL', determines how the boundaries are obtained
    :param proj: crs to project the boundary (using the default GHSL throughout the project, Mollweide)
    :param ghsl_gdf: GeoDataFrame, used if method is GHSL---otherwise full gdf is computed
    :param test: Boolean, whether this is the test run
    :param save: Boolean, whether the graph dictionary should be saved
    :param filepath: string, if saved file must be named in a particular way, default is graphs_dict.pickle
    
    return: dictionary with boundaries, keys are tuples (city, country)
    """
    
    #Get the boundary dictionary according to the given method:  
    if method == 'osmnx':
        boundaries_dict = get_boundaries_osmnx(cities, countries, proj)

    elif method == 'GHSL':
        boundaries_dict = get_boundaries_GHSL(ghsl_gdf)

    else:
        print('Invalid method. Only valid parameters are osmnx and GHSL.')
        return None
    
    #Saving the file:
    if save:
        if filepath is None:
            if test:
                filepath = '../data/test-run/boundaries_dict.pickle'
            else:
                filepath = '../data/d2_processed/boundaries_dict.pickle'
                
        with open(filepath, 'wb') as file:
            pkl.dump(boundaries_dict, file)
    
    return boundaries_dict

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':
    pass