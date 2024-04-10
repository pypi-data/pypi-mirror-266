"""
This experiment processes the aggregators dataset. This is orignally a dataset consisting of about 300k molecules 
that are annotated with a binary classification label that identifies them as either an aggregator or a 
non-aggregator.

This experiment in particular processes a modified version of this dataset which takes into account different 
protonation states. For a chemical environment with a given pH value, not all of the hydrogen atoms (protons) might 
be attached to the molecule, but instead some of the atoms might exist in their charged form. In this modified 
dataset all the molecules are replaced with all it's possible protonated versions under normal conditions.

**CHANGELOG**

20.10.23 - initial version
"""
import os
import pathlib
import typing as t

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from pycomex.functional.experiment import Experiment
from pycomex.utils import file_namespace, folder_path
from visual_graph_datasets.util import get_experiment_path

np.set_printoptions(precision=2)

PATH = pathlib.Path(__file__).parent.absolute()
ASSETS_PATH = os.path.join(PATH, 'assets')

# == SOURCE PARAMETERS ==
# These parameters determine how to handle the source CSV file of the dataset. There exists the possibility
# to define a file from the local system or to download a file from the VGD remote file share location.
# In this section one also has to determine, for example, the type of the source dataset (regression, 
# classification) and provide the names of the relevant columns in the CSV file.

# :param FILE_SHARE_PROVIDER:
#       The vgd file share provider from which to download the CSV file to be used as the source for the VGD
#       conversion. 
FILE_SHARE_PROVIDER: str = 'main'
# :param CSV_FILE_NAME:
#       The name of the CSV file to be used as the source for the dataset conversion.
#       This may be one of the following two things:
#       1. A valid absolute file path on the local system pointing to a CSV file to be used as the source for
#       the VGD conversion
#       2. A valid relative path to a CSV file stashed on the given vgd file share provider which will be
#       downloaded first and then processed.
CSV_FILE_NAME: str = 'source/aggregators_binary_protonated.csv'
# :param INDEX_COLUMN_NAME:
#       Optionally, this may define the string name of the CSV column which contains the integer index
#       associated with each dataset element. If this is not given, then integer indices will be randomly
#       generated for each element in the final VGD
INDEX_COLUMN_NAME: t.Optional[str] = None
# :param SMILES_COLUMN_NAME:
#       This has to be the string name of the CSV column which contains the SMILES string representation of
#       the molecule.
SMILES_COLUMN_NAME: str = 'smiles'
# :param TARGET_TYPE: 
#       This has to be the string name of the type of dataset that we are working with here. THis is either 
#       classification or regression.
TARGET_TYPE: str = 'classification'
# :param TARGET_COLUMN_NAMES:
#       This has to be a list that specifies the string names of all the columns of the source file that 
#       contain the information about the target value annotations. For a classification dataset all the 
#       possible classes have to be represented as their own columns and the corresponding values have 
#       to be either 0 or 1 to indicate whether that class applies for a given element or not.
TARGET_COLUMN_NAMES: t.List[str] = ['aggregator', 'nonaggregator']

# == DATASET PARAMETERS ==
# These parameters control aspects of the visual graph dataset creation process. This for example includes 
# the dimensions of the graph visualization images to be created or the name of the visual graph dataset 
# that should be given to the dataset folder.

# :param DATASET_NAME:
#       The name given to the visual graph dataset folder which will be created.
DATASET_NAME: str = 'aggregators_binary'
# :param IMAGE_WIDTH:
#       The width of the visualization images that will be created for all the elements, in pixels
IMAGE_WIDTH: int = 1000
# :param IMAGE_HEIGHT:
#       The height of the visualization images that will be created for all the elements, in pixels
IMAGE_HEIGHT: int = 1000
# :param DATASET_META:
#       This dict will be converted into the .meta.yml file which will be added to the final visual graph dataset
#       folder. This is an optional file, which can add additional meta information about the entire dataset
#       itself. Such as documentation in the form of a description of the dataset etc.
DATASET_META: t.Optional[dict] = {
    'version': '0.2.0',
    # A list of strings where each element is a description about the changes introduced in a newer
    # version of the dataset.
    'changelog': [
        '0.1.0 - 29.01.2023 - initial version',
        '0.2.0 - 01.06.2023 - Now uses the protonated version of the dataset.'
    ],
    # A general description about the dataset, which gives a general overview about where the data was
    # sampled from, what the input features look like, what the prediction target is etc...
    'description': (
        'large dataset consisting of organic compounds which are divided into two classes: aggregators '
        'and non-aggregators.'
    ),
    # A list of informative strings (best case containing URLS) which are used as references for the
    # dataset. This could for example be a reference to a paper where the dataset was first introduced
    # or a link to site where the raw data can be downloaded etc.
    'references': [
        'Library used for the processing and visualization of molecules. https://www.rdkit.org/',
    ],
    # A small description about how to interpret the visualizations which were created by this dataset.
    'visualization_description': (
        'Molecular graphs generated by RDKit based on the SMILES representation of the molecule.'
    ),
    # A dictionary, where the keys should be the integer indices of the target value vector for the dataset
    # and the values should be string descriptions of what the corresponding target value is about.
    'target_descriptions': {
        0: 'one-hot: aggregator class',
        1: 'one-hot: non-aggregator class'
    }
}
# :param GRAPH_METADATA_CALLBACKS:
#       This dictionary can be used to add additional functions that can extract data from the original molecule 
#       and csv data row objects to save as additonal metadata to the graph structure of the visual graph dataset.
GRAPH_METADATA_CALLBACKS = {
    # 'name': lambda mol, data: data['name'],
    # 'label': lambda mol, data: data['label'],
    'smiles': lambda mol, data: data['smiles'],
    'index_original': lambda mol, data: data['index_original'] if 'index_original' in data else data['index'],
    'smiles_origianl': lambda mol, data: data['smiles_orignal'] if 'smiles_orginal' in data else '',
}
# :param DATASET_CHUNK_SIZE:
#       Larger visual graph datasets will be saved in chunks, which means that the dataset folder itself
#       will not contain all the files directly but will rather consist of several chunk folders which then 
#       contain the actual data. This parameter controls how many files each chunk will consist of.
DATASET_CHUNK_SIZE: int = 10_000

# == EVALUATION PARAMETERS ==
# These parameters control the behavior of the various evaluation functions of the experiment which mainly 
# includes the logging and plotting facilities.

EVAL_LOG_STEP: int = 1000
NUM_BINS: int = 10
PLOT_COLOR: str = 'gray'

__DEBUG__ = False

experiment = Experiment.extend(
    # We can exploit the base implementation of the molecule dataset processing experiment that is already 
    # part of the visual_graph_dataset library.
    get_experiment_path('generate_molecule_dataset_from_csv.py'),
    base_path=folder_path(__file__),
    namespace=file_namespace(__file__),
    glob=globals()
)

experiment.run_if_main()
