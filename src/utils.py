#--------------------------------------------------------------------------------------------
# GOAL: define functions to be used throughout the project
#--------------------------------------------------------------------------------------------

import sys
sys.path.append('../')

import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

def load_file(filepath, ext=None):
    
    #Get the extension if none was provided:
    if ext is None:
        ext = filepath.split(".")[-1]
    
    if ext == 'pickle':
        with open(filepath, 'rb') as file:
            loaded_file = pkl.load(file)
        
    elif ext == 'csv':
        loaded_file = pd.read_csv(filepath)
        
    else:
        print('Please load file directly or manually input the extension')
        
    return loaded_file

def get_categorical_cmap(df, col, null_value=pd.NA, cmap=cm.tab10):

    keys = list(df[col].unique())
    color_range = list(np.linspace(0, 1, len(keys), endpoint=False))
    colors = [cmap(x) for x in color_range]
    color_dict = dict(zip(keys, colors))
    color_dict[null_value]='lightgrey'
    
    return color_dict