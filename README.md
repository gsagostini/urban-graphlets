# Graphlet Correlations for Street Networks of Worlwide Urban Centers

Abstract paragraph with project goals.

## Installation

To use the code in this repository, the creation of a new virtual environment is recommended. This can be done via the enviroment.yml file:
```
conda env create -f environment.yml
```
The environment `urban-graphlets` will be created and can be activated with `conda activate urban-graphlets`. Installation via `pip` is not recommend due to constraints in the OSMNx library.

Orbit counting and graphlet analysis relies on the Orbit Counting Algorithm [1]. The original implementation of the algorithm uses C++, so we make use of a python wrapper [2] hosted on the `src` directory. To install it, one must run:
```
cd src/
make
```

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
