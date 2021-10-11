#--------------------------------------------------------------------------------------------
# GOAL: obtain the list of cities (and respective countries) that will be used in the project
#--------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

import csv
import fiona
import geopandas as gpd

from src.vars import test_cities, ghsl_crs, urbancentre_filepath, cities_filepath

test=False

#--------------------------------------------------------------------------------------------

def get_urbancentre_gdf(raw_data_path=urbancentre_filepath, crs=ghsl_crs, method='Fiona'):
    """
    Gets a GeoDataFrame of urbancentres from GHSL data
    
    :param raw_data_path: string, filepath for raw data
    :param crs: crs, projection of GHSL data
    :param method: direct or Fiona, whether to load the geopackage directly or using Fiona
                    (currently recommend using Fiona)
    
    return GeoDataFrame
    """
    
    if method == 'direct':
        
        gdf = gpd.read_file(raw_data_path, to_crs=crs)
    
    elif method == 'Fiona':
        #Use Fiona to open the file (to avoid an issue with the crs)
        with fiona.open(raw_data_path, 'r') as fiona_collection:
            # Create GeoDataFrame from Fiona Collection
            gdf = gpd.GeoDataFrame.from_features([feature for feature in fiona_collection], crs=crs)
            # Get the order of the fields in the Fiona Collection; add geometry to the end
            columns = list(fiona_collection.meta["schema"]["properties"]) + ["geometry"]
            # Re-order columns in the correct order
            gdf = gdf[columns]
            
    return gdf

def clean_urbancentre_gdf(gdf,
                          columns=['UC_NM_MN', 'UC_NM_LST', 'CTR_MN_NM', 'GRGN_L1', 'GRGN_L2', 'P15', 'AREA', 'geometry'],
                          column_names={'UC_NM_MN':'urban centre',
                                          'UC_NM_LST':'cities',
                                          'CTR_MN_NM':'country',
                                          'GRGN_L1': 'continent',
                                          'GRGN_L2':'subcontinent',
                                          'P15':'population',
                                          'AREA':'area'}):
    """
    Select columns and rename them given a GeoDataFrame
    
    :param gdf: DataFrame to be cleaned
    :param columns: list of strings, columns of the data to keep
    :param column_names: dictionary, how to rename the columns
    
    return GeoDataFrame
    """    
    
    clean_gdf = gdf[columns]
    processed_gdf = clean_gdf.rename(column_names, axis='columns')
    
    return processed_gdf

def get_processed_urbancentre_gdf(raw_data_path=urbancentre_filepath,
                                  crs=ghsl_crs,
                                  columns=['UC_NM_MN', 'UC_NM_LST', 'CTR_MN_NM', 'GRGN_L1', 'GRGN_L2', 'P15', 'AREA', 'geometry'],
                                  column_names={'UC_NM_MN':'urban centre',
                                                  'UC_NM_LST':'cities',
                                                  'CTR_MN_NM':'country',
                                                  'GRGN_L1': 'continent',
                                                  'GRGN_L2':'subcontinent',
                                                  'P15':'population',
                                                  'AREA':'area'},
                                  sample=False,
                                  sampleby='subcontinent',
                                  maxnum=190,
                                  random_seed=0,
                                  method='Fiona'):
    """
    Gets a GeoDataFrame of urbancentres from GHSL data, cleans the columns, and samples the rows
    
    :param raw_data_path: string, filepath for raw data
    :param crs: crs, projection of GHSL data
    :param columns: list of strings, columns of the data to keep
    :param column_names: dictionary, how to rename the columns
    :param sample: Boolean, whether to subsample the dataframe
    :param sampleby: string (column name) or None, whether to keep the sample uniform across groups
    :param maxnum: int, top number of cities to keep
    
    return GeoDataFrame
    """
    
    #Get the GeoDataFrame and clean it:
    raw_gdf = get_urbancentre_gdf(raw_data_path, crs, method)
    processed_gdf = clean_urbancentre_gdf(raw_gdf, columns, column_names)
    
    #If we want to sample:
    if sample:
        
        if sampleby is None:
            sampled_gdf = processed_gdf.sample(n=maxnum, random_state=random_seed)
            
        else:
            #We separately implement the subcontinent case, to drop the 1 Polynesian urban centre:
            if sampleby == 'subcontinent':
                grouped_gdf = processed_gdf[processed_gdf['subcontinent'] != 'Polynesia'].groupby('subcontinent')
                sampled_gdf = grouped_gdf.sample(n=int(maxnum//grouped_gdf.ngroups), random_state=random_seed).reset_index()
            else:
                grouped_gdf = processed_gdf.groupby(sampleby)
                sampled_gdf = grouped_gdf.sample(n=int(maxnum//grouped_gdf.ngroups), random_state=random_seed).reset_index()
    else:
        sampled_gdf = processed_gdf
    
    return sampled_gdf

def read_cities_GHSL(ghsl_gdf=None,
                     raw_data_path=urbancentre_filepath,
                     crs=ghsl_crs,
                     columns=['UC_NM_MN', 'UC_NM_LST', 'CTR_MN_NM', 'GRGN_L1', 'GRGN_L2', 'P15', 'AREA', 'geometry'],
                     column_names={'UC_NM_MN':'urban centre',
                                   'UC_NM_LST':'cities',
                                   'CTR_MN_NM':'country',
                                   'GRGN_L1': 'continent',
                                   'GRGN_L2':'subcontinent',
                                   'P15':'population',
                                   'AREA':'area'},
                    method='Fiona'):
    """
    Gets a list of cities and a list of countries from the GHSL dataset
    
    :param ghsl_gdf: GHSL processed dataframe, if None then must be obtained and next arguments are passed to function
    
    return: list of cities, list of countries (respectively)
    """
                     
    #In case we did not pass the GeoDataFrame we must find it:
    if ghsl_gdf is None:
        raw_gdf = get_urbancentre_gdf(raw_data_path, crs, method)
        ghsl_gdf = clean_urbancentre_gdf(raw_gdf, columns, column_names)
    
    cities = list(ghsl_gdf['urban centre'])
    countries = list(ghsl_gdf['country'])    
    
    return cities, countries

def read_cities_csv(cities_filepath=cities_filepath, dlm=';'):
    """
    Gets a list of cities and a list of countries from the csv file provided
    
    return: list of cities, list of countries (respectively)
    """
    
    cities = []
    countries = []
    with open(cities_filepath) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=dlm)
        next(readCSV)
        for row in readCSV:
            cities.append(row[1].replace('_', ' '))
            countries.append(row[2].replace('_', ' '))
    
    return cities, countries  
    
def get_cities_and_countries(test=test, method='GHSL', ghsl_gdf=None, method_GHSL='Fiona', cities_filepath=cities_filepath):
    """
    Gets a list of cities and a list of countries that will be used in the experiments
    
    :param test: Boolean, whether this is the test run
    
    return: list of cities, list of countries (respectively)
    """
    #In case this is the test run, we deal with the pre-defined cities:
    if test:
        from src.vars import test_cities
        cities, countries = zip(*test_cities)
        
    #Else, we must read the list provided:
    else:
        if method=='GHSL':
            cities, countries = read_cities_GHSL(ghsl_gdf, method=method_GHSL)
        elif method=='csv':
            cities, countries = read_cities_csv(cities_filepath)
        
    return cities, countries

#--------------------------------------------------------------------------------------------

if __name__== '__main__':
    pass