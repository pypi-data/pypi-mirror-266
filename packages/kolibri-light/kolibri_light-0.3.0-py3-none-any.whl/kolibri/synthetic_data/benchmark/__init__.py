"""SDGym - Synthetic data Gym.

SDGym is a framework to benchmark the performance of synthetic data generators for
tabular data.
"""

__author__ = 'DataCebo, Inc.'
__copyright__ = 'Copyright (c) 2022 DataCebo, Inc.'
__email__ = 'info@sdv.dev'
__license__ = 'BSL-1.1'
__version__ = '0.7.1.dev0'

import logging

from kolibri.synthetic_data.benchmark.benchmark import run
from kolibri.synthetic_data.benchmark.data import load_original_dataset, load_synthetic_dataset
from kolibri.synthetic_data.benchmark.synthesizers import create_sdv_synthesizer_variant, create_single_table_synthesizer
from kolibri.synthetic_data.benchmark.utility import fidelity
from kolibri.synthetic_data.benchmark.privacy import privacy
from kolibri.synthetic_data.benchmark.ml import train_model, evaluate_model
# Clear the logging wrongfully configured by tensorflow/absl
list(map(logging.root.removeHandler, logging.root.handlers))
list(map(logging.root.removeFilter, logging.root.filters))

__all__ = [
    'load_original_dataset',
    'load_synthetic_dataset',
    'run',
    'create_sdv_synthesizer_variant',
    'create_single_table_synthesizer',
    'fidelity',
    'train_model',
    'evaluate_model'
]
