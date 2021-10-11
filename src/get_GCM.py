#--------------------------------------------------------------------------------------------
# GOAL: obtain a GeoDataFrame containing tiles and their Graphlet Correlation Matrices (GCMs)
#--------------------------------------------------------------------------------------------

import pickle as pkl
import sys
sys.path.append('../')

import numpy as np
import pandas as pd
from tqdm import tqdm

from scipy import stats
import networkx as nx

import geopandas as gpd
import osmnx as ox

import rasterio as rio
from rasterio.mask import mask

from shapely.geometry import shape
from shapely.geometry import Polygon

from src.utils import load_file
from src.vars import ghsl_data, ghsl_crs, redundant_orbits, ghsl_resolution

test=False

#--------------------------------------------------------------------------------------------

def trim_GDV(GDV, redundant_orbits=redundant_orbits):
    trim = [GDV[i] for i in range(15) if i not in redundant_orbits]
    return trim

def trim_GDM(GDM, redundant_orbits=redundant_orbits):
    GDM_11 = []
    for GDV in GDM:
        GDV_11 = trim_GDV(GDV, redundant_orbits)
        GDM_11.append(GDV_11)
    return GDM_11

def get_GCM(GDM):
    """
    Gets the Graphlet Correlation Matrix of a network from its Graphlet Degree Matrix
    
    :param GDM: array, the full Graphlet Degree Matrix of the network
    
    return: array, the 11x11 Graphlet Correlation Matrix
    """
    
    if GDM is None or GDM.size == 0:
        return None
    
    GDM_trimmed = trim_GDM(GDM)
    new_GDM = GDM_trimmed.copy()
    length = len(new_GDM[0])
    
    # Add the dummy signature for some noise
    new_GDM.append([1] * length)
    
    # Compute the ranking for the Spearman's correlation coefficient computation
    rankList = []
    for i in range(length):
        rankList.append(stats.mstats.rankdata([val[i] for val in new_GDM]))
    GCM = np.corrcoef(rankList, rowvar = 1)
    
    return GCM

def clip_raster(raster_data, boundary_geometry, filepath=None):
    """
    Clips raster data according to Polygon and saves the file
    
    :param raster_data: rasterio DatasetReader object
    :param geometry: geometry of the city boundary
    :param filename: string, if saved file must be named in a particular way, default is clipped_raster.tif
    
    return: rasterio DatasetReader object
    """
    #Project the boundary:
    boundary_proj = boundary_geometry.to_crs(raster_data.crs)['geometry']
    
    #Get the masked data:
    out_image, out_transform = mask(raster_data, boundary_proj, crop=True)
    out_meta = raster_data.meta
    out_meta.update({'driver': 'GTiff',
                     'height': out_image.shape[1],
                     'width': out_image.shape[2],
                     'transform': out_transform,
                     'array': out_image})    
    
    #Save the raster file:
    if filepath is None:
        filepath = '../data/d2_processed/clipped_raster.tif'
    
    with rio.open(filepath, 'w', **out_meta) as dest:
        dest.write(out_image)
    
    #Open the file and return it:
    clipped_raster = rio.open(filepath)
    
    return clipped_raster

def get_ghsl_gdf_contiguous(ghsl_raster_data, value_name='classification'):
    """
    Transforms raster data into GeoDataFrame with 'geometry' and 'classification' (values) columns, each 
     geometry corresponds to a contiguous zone according to the raster values
    
    :param ghsl_raster_data: rasterio DatasetReader object
    :param value_name: string
    
    return: GeoDataFrame object with all the tile geometries
    """
    
    #Read the data and get contiguous shapes:
    shapes = rio.features.shapes(ghsl_raster_data.read(1))
    #Read the shapes and values as separate lists:
    values = []
    geometries = []
    for shapedict, value in shapes:
        values.append(value)
        geometries.append(shape(shapedict))
    
    #Replace the value for NaN where appropriate:
    values_processed = np.where(values == ghsl_raster_data.nodata, np.nan, values)
    
    #Creat the GeoDataFrame and return:
    gdf = gpd.GeoDataFrame({value_name: values_processed, 'geometry': geometries},
                           crs=ghsl_raster_data.crs)

    return gdf

def get_ghsl_gdf(ghsl_raster_data, value_name='classification', box_len=ghsl_resolution):
    """
    Transforms raster data into GeoDataFrame with 'geometry' and 'classification' (values) columns, each
     geometry corresponds to a pixel
    
    :param ghsl_raster_data: rasterio DatasetReader object
    :param value_name: string
    :param box_len: tuple of ints, length of a GHSL tile i.e. resolution of the raster data. Default is 1km.
    
    return: GeoDataFrame object with all the tile geometries
    """
    
    #Get the values:
    values_arr = ghsl_raster_data.read(1)
    values = values_arr.flatten()
    values_processed = np.where(values == ghsl_raster_data.nodata, np.nan, values)
    
    #Get the box corners using the affine transformation:    
    box_width = box_len[0]
    box_height = box_len[1]
    geometries = []
    for row_idx in range(ghsl_raster_data.height):
        for col_idx in range(ghsl_raster_data.width):
            ul_x, ul_y = ghsl_raster_data.xy(row_idx, col_idx, offset='ul')
            box = [(ul_x, ul_y),
                  (ul_x + box_width, ul_y),
                  (ul_x + box_width, ul_y - box_height),
                  (ul_x, ul_y - box_height)]
            geometries.append(Polygon(box))
            
    #Creat the GeoDataFrame and return:
    gdf = gpd.GeoDataFrame({value_name: values_processed, 'geometry': geometries},
                           crs=ghsl_raster_data.crs)

    return gdf

def get_polygon_GDM(polygon, node_gdf, full_GDM=None):
    """
    Obtains the Graphlet Degree Matrix (GDM) of the network inside a polygon
    
    :param polygon: boundary to obtain the GDM in
    :param nodes_gdf: GeoDataFrame of all N nodes (geometries are points)
    :full_GDM: np.array of shape N x 11, if None then nodes_gdf must contain the GDV of each node
    
    return: np.array of shape n x 11 (n is the number of nodes inside the polygon)
    """
    
    #Get the GDM if we do not have it:
    if full_GDM is None:
        full_GDM = np.stack(node_gdf['GDV'].values)
    
    #Find what nodes are inside the polygon:
    node_is_within_polygon_arr = node_gdf.within(polygon).to_numpy()
    
    #Trim the GDM and return:
    polygon_GDM = full_GDM[node_is_within_polygon_arr]
    return polygon_GDM

def refine_city_gdf(city_gdf, city, country):
    """
    Prepares each city's GHSL GeoDataFrame to the combinated gdf
    
    :param city_gdf: GeoDataFrame of GHSL tiles containing their GCM and classification
    :param city: string
    :param country: string
    
    return: GeoDataFrame without null rows and extra columns
    """
    
    #Drop null tiles and tiles that are not in the city boundary:
    city_gdf.dropna(subset=['classification', 'GCM'], inplace=True)
    
    #Add a column for city and a column for country:
    city_gdf['city'] = city
    city_gdf['country'] = country
    
    #Add a column to flag tiles with valid GCM (only finite values):
    city_gdf['valid_GCM'] = city_gdf['GCM'].apply(lambda x: ~np.isnan(x).any())
    
    return city_gdf    

def get_ghsl_geodataframe(node_gdfs_dict, boundaries_dict,
                          ghsl_data=ghsl_data, proj=ghsl_crs,
                          test=test,
                          save=True, filepath=None):
    """
    Get GeoDataFrame of GHSL tiles
    
    :param nodes_gdfs_dict: dictionary with node geodataframes, keys are tuples (city, country)
    :param boundaries_dict: dictionary with city boundaries, keys are tuples (city, country)
    :param ghsl_data: raster data from GHSL with classification
    :param proj: crs to project the gdf (using the default GHSL throughout the project, Mollweide)
    :param test: Boolean, whether this is the test run
    :param save: Boolean, whether the geodataframe should be saved
    :param filepath: string, filepath if non-default path is desired
    
    return: GeoDataFrame with all GHSL tiles with columns
            - classification: degree of urbanization according to GHSL documentation
            - GDM: Graphlet Degree Matrix for nodes in that tile
            - GCM: Graphlet Correlation Matrix (11x11) for that tile
            - valid_GCM: Boolean Series, flags tiles with valid GCM (only finite values) 
            - city, country: identification of the tile
    """
    
    if filepath is None:
        if test:
            filepath = '../data/test-run/tiles_gdf.pickle'
        else:
            filepath = '../data/d2_processed/tiles_gdf.pickle'
            
    #Maybe the ghsl tiles gdf already begun to be available, so we load it and add to list:    
    try:
        ghsl_tiles_gdf = load_file(filepath)
        ghsl_gdfs = [ghsl_tiles_gdf]
        existing_cities = list(set(ghsl_tiles_gdf['city']))
    except FileNotFoundError:
        ghsl_gdfs = []
        existing_cities = []
    
    na_counter=1  #for cities named N/A
    
    for city, country in tqdm(node_gdfs_dict.keys()):
        
        
        #Retriving city information:
        node_gdf = node_gdfs_dict[(city, country)]
        boundary_polygon = boundaries_dict[(city, country)][['geometry']]
        
        if node_gdf is not None and city not in existing_cities: #and city not in ['Tokyo', 'Algiers', 'London']:
        
            #We will save the clipped rasters, so we must know the filename:
            if '/' in city:
                clipped_raster_filename = 'NA' + str(na_counter) + '_' + country
                na_counter += 1
            else:
                clipped_raster_filename = city + '_' + country
                
            if test:
                clipped_raster_filepath = '../data/test-run/cities-GHSL/' + clipped_raster_filename + '.tif'
            else:
                clipped_raster_filepath = '../data/d2_processed/cities-GHSL/' + clipped_raster_filename + '.tif'


            #Get the clipped raster according to city boundary and the GHSL gdf:
            clipped_raster = clip_raster(ghsl_data, boundary_polygon, filepath=clipped_raster_filepath)
            ghsl_gdf = get_ghsl_gdf(clipped_raster)

            #Get the GDM of each tile and add the column to the GeoDataFrame:
            full_GDM = np.stack(node_gdf['GDV'].values)
            ghsl_gdf['GDM'] = ghsl_gdf['geometry'].apply(get_polygon_GDM, node_gdf=node_gdf, full_GDM=full_GDM)

            #Get the GCM of each tile:
            ghsl_gdf['GCM'] = ghsl_gdf['GDM'].apply(get_GCM)

            #Refine the gdf:
            new_ghsl_gdf = refine_city_gdf(ghsl_gdf, city, country)

            #Add the GeoDataFrame to our list:
            ghsl_gdfs.append(ghsl_gdf)
        
    
            #Concatenate vertically all the GHSL gdfs
            ghsl_gdf = gpd.GeoDataFrame(pd.concat(ghsl_gdfs, ignore_index=True)).to_crs(proj)

            if save:
                if filepath is None:
                    if test:
                        filepath = '../data/test-run/tiles_gdf.pickle'
                    else:
                        filepath = '../data/d2_processed/tiles_gdf.pickle'

                with open(filepath, 'wb') as file:
                    pkl.dump(ghsl_gdf, file)
    
    return ghsl_gdf

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':
    pass