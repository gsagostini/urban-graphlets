#--------------------------------------------------------------------------------------------
# GOAL: obtain the simplified street network inside each polygon (city boundary)
#--------------------------------------------------------------------------------------------

import pickle as pkl
from tqdm import tqdm
import sys
sys.path.append('../')

import networkx as nx
import osmnx as ox

from src.vars import ghsl_crs, tolerance
from src.utils import load_file

test=False

#--------------------------------------------------------------------------------------------

def find_duplicates(edge_list):
    """
    Finds parallel edges in the graph
    
    :param edge_list: list of edges, i.e. tuples of two nodes
    
    return: list of duplicated edges, i.e. tuples of two nodes
    """
    #We create a list to add duplicates, and a dictionary to count how many
    # times the object appears:
    seen = dict()
    duplicates = []
    #Now iterate over elements of the list:
    for edge in edge_list:
        #In case it is the first time an element appears
        if edge not in seen:
            seen[edge] = 1
        #In case we have seen the element before
        else:
            duplicates.append(edge)
            seen[edge] += 1    #Note that if an edge appears say three times
                               # then it appears twice in the duplicate list!
    return duplicates

def simplify_graph(graph, tol=tolerance):
    """
    Simplify graph by consolidating intersections, removing direction, removing duplicate edges,
      and removing self-loops
    
    :param graph: osmnx.MultiGraph, raw street network
    :param tol: float, distance (in meters) within which nodes are deemed indistinguishable
    
    return: osmnx.Graph, cleaned street network
    """
    #First we need to project it so we can run the OSMNx functions:
    H = ox.project_graph(graph)
    #Now consolidate intersections, using tolerance provided, default is 15:
    H1 = ox.consolidate_intersections(H, tolerance=tol, dead_ends=True)
    #Now we remove the direction and merge some edges along the way:
    H2 = ox.get_undirected(H1)
    #Now we remove parallel edges:
    dup = find_duplicates(H2.edges())
    H3 = H2.copy()
    H3.remove_edges_from(dup)
    #Finally, let's remove the selfloops:
    H4 = H3.copy()
    sl = list(nx.selfloop_edges(H4))
    H4.remove_edges_from(sl)
    """
    UPDATE: Solved in 2021/01 update to OSMNx
    #Consolidating intersections will turn some osmids into non-integers, so
    # we need to fix that:
    for node in H4.nodes(data='osmid'):
        osmid = node[1]
        if type(osmid) != np.int64:
            if '[' in osmid:
                osmid = osmid.strip('][').split(', ')[0]
            if '-' in osmid:
                osmid = osmid.split('-')[0]
            H4.nodes[node[0]]['osmid'] = int(osmid)  
    """
    #This is the graph we want, so let's return it:
    return H4  

def get_graphs(boundaries_dict, proj=ghsl_crs, test=test, save=True, filepath=None):
    """
    Get simplified street networks for all polygons provided.
    
    :param boundaries_dict: dictionary with polygons, keys are tuples (city, country)
    :param proj: crs to project the graph (using the default GHSL throughout the project, Mollweide)
    :param test: Boolean, whether this is the test run
    :param save: Boolean, whether the graph dictionary should be saved
    :param filepath: string, if saved file must be named in a particular way, default is graphs_dict.pickle
    
    return: dictionary with graphs, keys are tuples (city, country)
    """
    if filepath is None:
        if test:
            filepath = '../data/test-run/graphs_dict.pickle'
        else:
            filepath = '../data/d2_processed/graphs_dict.pickle'
    #Maybe the graphs dictionary is already available, so we load it:    
    try:
        graphs_dict = load_file(filepath)
    except:
        graphs_dict = dict()
    
    #Iterate over all cities in the boundaries dictionary that are not in the dict yet:
    for city, country in tqdm(boundaries_dict.keys()):
        
        if (city, country) not in graphs_dict.keys() and city != 'Tokyo':
        
            boundary = boundaries_dict[(city, country)]['geometry'][0]
            try:
                graph = ox.graph_from_polygon(boundary, network_type='drive')

                simplified_graph = simplify_graph(graph)

                simplified_graph_proj = ox.project_graph(simplified_graph, to_crs=proj)

                graphs_dict[(city, country)] = simplified_graph_proj
            except:
                print("Problem in the graph of ", city, ",", country)
                graphs_dict[(city, country)] = None

            #Save at every step to avoid issues.
            if save:
                with open(filepath, 'wb') as file:
                    pkl.dump(graphs_dict, file)
    
    return graphs_dict

#--------------------------------------------------------------------------------------------

if __name__== '__main__':
    pass