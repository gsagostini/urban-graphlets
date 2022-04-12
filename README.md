# Graphlet Analysis for Street Networks of Worlwide Urban Centers

Street networks encompass much of the visual identity we attribute to cities. The gridded blocks of North-American metropoles, the narrow disorganized streets of Brazilian favelas, and the coencentric circles of European historical districts carry morphological information of those cities that may reveal interesting patterns of accessibility and urban growth. Thinking of street networks as composed of small connected subgraphs—graphlets: a square block, a path of three streets, a triangle—we would like to identify building blocks of cities. This is a common technique in biological and social networks, where the graphlets (or motifs) have been shown to correlate with the function or type of the network. Looking at graphlets of up to 4 nodes in the street networks of New York City, we identify local structures such as gridded patches through spatial auto-correlation statistics. This methodology can be quickly applied to any city in the world, helping researchers classify local street structures and identify common urban development trends across many cities.

## Installation

To use the code in this repository, the creation of a new virtual environment is recommended. This can be done via the enviroment.yml file:
```
conda env create -f environment.yml
```
The environment `urban-graphlets` will be created and can be activated with `conda activate urban-graphlets`. Installation via `pip` is not recommend due to constraints in the OSMNx library.

Orbit counting and graphlet analysis relies on the Orbit Counting Algorithm [1]. The original implementation of the algorithm uses C++, so we make use of a python wrapper [2] hosted on the `src` directory. To install it, one must run:
```
cd src/orcalib/
make
```
Orca may now be imported as a Python module via the comand `from src.orcalib import orca`.

## Repository Setup

```
├── README.md                      <- README with project goals and installation guidelines.
│
├── environment.yml                <- Environment export generated with `conda env export > environment.yml`
│
├── .gitignore                     <- Avoids uploading certain files
│
├── data
│   ├── d1_raw               
│   ├── d2_processed
│   └── d3_results
│
├── notebooks                      <- Jupyter notebooks. Naming convention is date MMDD (for ordering) and a short description.
│
├── src                            <- Source code for use in this project, which can be imported as modules into the notebooks and scripts.
│
└── scripts                        <- Scripts which perform a series of tasks.

```

(To be explained further)

## Data Sources

## References

[1] Hočevar, T., Demšar, J., 2014: A combinatorial approach to graphlet counting, _Bioinformatics_ 30 (4),559–565, doi.org/10.1093/bioinformatics/btt717

[2] Wang, A., Ying, R., 2020: _PyORCA: OrCA orbit Counting Python Wrapper_. github.com/qema/orca-py.
