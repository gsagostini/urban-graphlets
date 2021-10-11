#--------------------------------------------------------------------------------------------
# GOAL: define variables and paths to be used throughout the project
#--------------------------------------------------------------------------------------------

"""
test_cities: list of tuples (city, country)
             cities to be used when the testrun notebooks is considered
"""
test_cities =  [('The Hague', 'Netherlands'),
                ('New York', 'USA'),
                ('Porto Alegre', 'Brazil'),
                ('Delhi', 'India'),
                ('Moscow', 'Russia'),
                ('Beijing', 'China'),
                ('Rio de Janeiro', 'Brazil'),
                ('Lagos', 'Nigeria'),
                ('Paris', 'France'),
                ('Buenos Aires', 'Argentina'),
                ('Budapest', 'Hungary'),
                ('Nairobi', 'Kenya')]

"""
ghsl_data: raster reader
           GHSL data, whose first band contains the information of interest
ghsl_crs: crs
          projection of the GHSL data (Mollweide), which will standardize projections across the scripts
"""
import rasterio
ghsl_data = rasterio.open('../data/d1_raw/raster-tiles/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif')
ghsl_crs = ghsl_data.crs

"""
urbancentre_filepath: GHSL data on urban centres
"""
urbancentre_filepath = '../data/d1_raw/urban-centre-database/GHS_STAT_UCDB2015MT_GLOBE_R2019A_V1_2.gpkg'

"""
cities_filepath: manual list of cities; countries; continents
"""
cities_filepath = '../data/d1_raw/list_of_cities.csv'


"""
tolerance: float
           distance (in meters) around a node in the street network within which all nodes are merged
"""
tolerance = 15

"""
redundant_orbits: array of integers
                  indices of orbits that are not relevant in the GCM computation
"""
redundant_orbits = [3, 12, 13, 14]

"""
ghsl_resolution: tuple of floats
                 length and width of a GHSL raster pixel, in meters
"""
ghsl_resolution = (1000,1000)


"""
available_metrics: list of strings
                   metrics available in the scipy pdist function, which will be called when constructing the clustering linkage matrix
"""
available_metrics = ['braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation', 'cosine', 'dice', 'euclidean',
                     'hamming', 'jaccard', 'jensenshannon', 'kulsinski', 'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto',
                     'russellrao', 'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule']