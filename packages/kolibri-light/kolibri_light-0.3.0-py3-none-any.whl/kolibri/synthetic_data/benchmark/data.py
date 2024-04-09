
import itertools
import json
import logging
import os, sys
import pandas as pd
from pathlib import Path
import pickle
import tracemalloc
from datetime import datetime
from kolibri.datasets import get_data
from kolibri.synthetic_data.metadata import TableMetadata
from kolibri.synthetic_data.benchmark.reporting import generate_quality_report
from kolibri.synthetic_data.benchmark.synthesizers.base import BaselineSynthesizer
from kolibri.synthetic_data.benchmark.utils import get_synthesizers
from sklearn.model_selection import train_test_split
import gc


LOGGER = logging.getLogger(__name__)
N_BYTES_IN_MB = 1000 * 1000

def _get_dataset_subset(data, metadata_dict, max_rows=1000, max_columns=10):

    columns = metadata_dict['columns']
    if len(columns) > max_columns:
        columns = dict(itertools.islice(columns.items(), max_columns))
        metadata_dict['columns'] = columns
        data = data[columns.keys()]

    data = data.head(max_rows)

    return data, metadata_dict


def load_original_dataset(dataset_path, limit_dataset_size=None):

    with open(dataset_path) as data_csv:
        data = pd.read_csv(data_csv)

    stem=Path(dataset_path).stem
    base_path=Path(dataset_path).parent
    metadata_filename = stem+'_metadata.json'
    if not os.path.exists(f'{base_path}/{metadata_filename}'):
        raise Exception('Metadata file absent')

    with open(base_path / metadata_filename) as metadata_file:
        metadata_dict = json.load(metadata_file)

    if limit_dataset_size:
        data, metadata_dict = _get_dataset_subset(data, metadata_dict)

    return data, metadata_dict


def load_synthetic_dataset(dataset_path):

    with open(dataset_path) as data_csv:
        data = pd.read_csv(data_csv)

    stem=Path(dataset_path).stem
    output_filename = stem+'_output.json'
    base_path=Path(dataset_path).parent
    if not os.path.exists(f'{base_path}/{output_filename}'):
        raise Exception('Output file absent')

    with open(base_path / output_filename) as metadata_file:
        output_dict = json.load(metadata_file)


    return data, output_dict

def _synthesize_data(synthesizer_dict, real_data, metadata):
    synthesizer = synthesizer_dict['synthesizer_name']
    synthesizer_kw=synthesizer_dict['kwargs']
    assert issubclass(
        synthesizer, BaselineSynthesizer), '`synthesizer_name` must be a synthesizer_name class'

    synthesizer_object = synthesizer()
    get_synthesizer = synthesizer_object.get_trained_synthesizer
    sample_from_synthesizer = synthesizer_object.sample_from_synthesizer
    data = real_data.copy()
    num_samples = len(data)

    tracemalloc.start()
    now = datetime.utcnow()
    synthesizer_obj = get_synthesizer(data, metadata, **synthesizer_kw)
    try:
        synthesizer_size = len(pickle.dumps(synthesizer_obj)) / N_BYTES_IN_MB
    except:
        synthesizer_size = sys.getsizeof(synthesizer_obj)
    train_now = datetime.utcnow()
    synthetic_data = sample_from_synthesizer(synthesizer_obj, num_samples)
    sample_now = datetime.utcnow()

    peak_memory = tracemalloc.get_traced_memory()[1] / N_BYTES_IN_MB
    tracemalloc.stop()
    tracemalloc.clear_traces()

    return synthetic_data, train_now - now, sample_now - train_now, synthesizer_size, peak_memory

def _create_results_directory(detailed_results_folder):
    if detailed_results_folder:
        detailed_results_folder = Path(detailed_results_folder)
        os.makedirs(detailed_results_folder, exist_ok=True)
        if not os.path.exists(os.path.join(detailed_results_folder, 'original_data')):
            os.makedirs(os.path.join(detailed_results_folder, 'original_data'), exist_ok=True)
            os.makedirs(os.path.join(detailed_results_folder, 'synthetic_data'), exist_ok=True)

def create_synthetic_data_experiments(synthesizers,  custom_synthesizers = [], results_folder="./data", kolibri_datasets=[], additional_datasets=[], quality_report=False, split_data_set=True):

    synthesizers = [] if synthesizers is None else synthesizers
    custom_synthesizers = [] if custom_synthesizers is None else custom_synthesizers
    synthesizers = get_synthesizers(synthesizers + custom_synthesizers)
    datasets=kolibri_datasets+additional_datasets
    _create_results_directory(results_folder)

    for dataset in datasets:
        try:
            data, dataset_name = (get_data(dataset), dataset) if dataset in kolibri_datasets else (pd.read_csv(datasets), Path(datasets).stem)
            data_path=os.path.join(results_folder, 'original_data', dataset_name + '.csv')
            data.to_csv(data_path,index=False)
            if split_data_set:
                data, val= train_test_split(data, test_size=0.5)
                data.to_csv(os.path.join(results_folder, 'original_data', dataset_name + '_train.csv'),index=False)
                val.to_csv(os.path.join(results_folder, 'original_data', dataset_name + '_val.csv'),index=False)

            metadata = TableMetadata()
            metadata.detect_from_dataframe(data=data)
            if os.path.exists(os.path.join(results_folder, 'original_data', dataset_name + '_metadata.json')):
                os.remove(os.path.join(results_folder, 'original_data', dataset_name + '_metadata.json'))
            metadata.save_to_json(os.path.join(results_folder, 'original_data', dataset_name + '_metadata.json'))
            for synthesizer in synthesizers:
                synthetic_data, train_time, sample_time, synthesizer_size, peak_memory=_synthesize_data(synthesizer, data, metadata)
                synthetic_data.to_csv(os.path.join(results_folder, 'synthetic_data', synthesizer["name"] + "_" + dataset_name + '.csv'), index=False)
                if quality_report:
                    generate_quality_report(data, synthetic_data, metadata.to_dict(), os.path.join(results_folder, 'synthetic_data', synthesizer["name"] + "_" + dataset_name), "quality_report")
                output={}
                output["train_time"]=train_time.seconds
                output["sample_time_ms"]=sample_time.microseconds
                output["synthesizer_size"]=synthesizer_size
                output["peak_memory"]=peak_memory
                with open(os.path.join(results_folder, 'synthetic_data', synthesizer['name'] + '_' + dataset_name + '_output.json'), 'w') as fp:
                    json.dump(output, fp)
                    print('dictionary saved successfully to file')
            gc.collect()
        except Exception as e:
            if e is not None:
                print(e)
            raise Exception('Failed to read dataset: '+dataset+"\n")
        if data is None:
            continue

