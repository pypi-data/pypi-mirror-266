"""Main SDGym benchmarking module."""

import concurrent
import logging
import multiprocessing
import os, json
import pathlib

import warnings
from datetime import datetime
from pathlib import Path
import sys, gc
import compress_pickle
import numpy as np
import pandas as pd
import tqdm
from sdmetrics.reports.single_table import QualityReport as SingleTableQualityReport
from os import listdir
from os.path import isfile, join
from kolibri.datasets import get_data
from kolibri.synthetic_data.benchmark.data import load_original_dataset, load_synthetic_dataset
from kolibri.synthetic_data.metadata import TableMetadata
from kolibri.utils import write_file, write_csv
from kolibri.synthetic_data.benchmark.reporting import generate_quality_report
from kolibri.synthetic_data.benchmark.metrics import get_metrics
from kolibri.synthetic_data.benchmark.synthesizers import CTGANSynthesizer, FastMLPreset, GaussianCopulaSynthesizer

from kolibri.synthetic_data.benchmark.utils import (
    format_exception, get_duplicates, get_num_gpus, get_size_of, get_synthesizers, used_memory)

LOGGER = logging.getLogger(__name__)
DEFAULT_SYNTHESIZERS = [GaussianCopulaSynthesizer, FastMLPreset, CTGANSynthesizer]
DEFAULT_DATASETS = [
#    'adult',
    # 'alarm',
    'census',
    # 'child',
    # 'expedia_hotel_logs',
    # 'insurance',
    # 'intrusion',
    # 'news',
    # 'covtype',
]
DEFAULT_METRICS = [('NewRowSynthesis', {'synthetic_sample_size': 1000})]
N_BYTES_IN_MB = 1000 * 1000


def _validate_inputs(output_filepath, detailed_results_folder, synthesizers, custom_synthesizers):
    if output_filepath and os.path.exists(output_filepath):
        raise ValueError(
            f'{output_filepath} already exists. '
            'Please provide a file that does not already exist.'
        )

    if detailed_results_folder and os.path.exists(detailed_results_folder):
        raise ValueError(
            f'{detailed_results_folder} already exists. '
            'Please provide a folder that does not already exist.'
        )

    duplicates = get_duplicates(synthesizers) if synthesizers else {}
    if custom_synthesizers:
        duplicates.update(get_duplicates(custom_synthesizers))
    if len(duplicates) > 0:
        raise ValueError(
            'Synthesizers must be unique. Please remove repeated values in the `synthesizers_dict` '
            'and `custom_synthesizers` parameters.'
        )


def _create_results_directory(detailed_results_folder):
    if detailed_results_folder:
        detailed_results_folder = Path(detailed_results_folder)
        os.makedirs(detailed_results_folder, exist_ok=True)
        os.makedirs(os.path.join(detailed_results_folder, 'original_data'))
        os.makedirs(os.path.join(detailed_results_folder, 'synthetic_data'))
def _run_all_scores(kolibri_datasets, additional_datasets_folder,
                    sdmetrics, detailed_results_folder, timeout,
                    compute_quality_score, synthesizers, custom_synthesizers):
    # Get list of synthesizer_name objects
    synthesizers = [] if synthesizers is None else synthesizers
    custom_synthesizers = [] if custom_synthesizers is None else custom_synthesizers
    synthesizers = get_synthesizers(synthesizers + custom_synthesizers)

    if additional_datasets_folder:
        additional_datasets = [f for f in listdir(additional_datasets_folder) if isfile(join(additional_datasets_folder, f))]
    else:
        additional_datasets=[]
    datasets=kolibri_datasets+additional_datasets
    job_tuples=[]
    for dataset in datasets:
        try:
            data, dataset_name = (get_data(dataset), dataset) if dataset in kolibri_datasets else (pd.read_csv(datasets), Path(datasets).stem)
            data_path=os.path.join(detailed_results_folder, 'original_data', dataset_name+'.csv')
            data.to_csv(data_path,index=False)
            metadata = TableMetadata()
            metadata.detect_from_dataframe(data=data)
            metadata.save_to_json(os.path.join(detailed_results_folder, 'original_data', dataset_name+'_metadata.json'))
            for synthesizer in synthesizers:
                job_tuples.append(( data_path, synthesizer))
                synthetic_data, train_time, sample_time, synthesizer_size, peak_memory=_synthesize_data(synthesizer, data, metadata)
                synthetic_data.to_csv(os.path.join(detailed_results_folder, 'synthetic_data', synthesizer["name"]+"_"+dataset_name + '.csv'),index=False)
                generate_quality_report(data, synthetic_data, metadata.to_dict(), os.path.join(detailed_results_folder, 'synthetic_data', synthesizer["name"]+"_"+dataset_name), "quality_report")
                output={}
                output["train_time"]=train_time.seconds
                output["sample_time_ms"]=sample_time.microseconds
                output["synthesizer_size"]=synthesizer_size
                output["peak_memory"]=peak_memory
                with open(os.path.join(detailed_results_folder, 'synthetic_data', synthesizer['name']+'_'+dataset_name + '_output.json'), 'w') as fp:
                    json.dump(output, fp)
                    print('dictionary saved successfully to file')
            gc.collect()
        except Exception as e:
            if e is not None:
                print(e)
            raise Exception('Failed to read dataset: '+dataset+"\n")
        if data is None:
            continue


    scores = []
    #keeps track to previously loaded data in order not to loaded again
    previous_data_set=None
    for dataset, synthesizer in tqdm.tqdm(job_tuples, total=len(job_tuples), position=0, leave=True):
        if previous_data_set != dataset:
            original_data, metadata= load_original_dataset(dataset)
            previous_data_set=dataset


        scores.append(_run_job(synthesizer,
                               original_data,
                               metadata,
                               sdmetrics,
                               detailed_results_folder,
                               timeout,
                               compute_quality_score,
                               dataset,
                               detailed_results_folder))

    return scores





def _compute_scores(metrics, real_data, synthetic_data, metadata,
                    output, compute_quality_score, dataset_name):
    metrics = metrics or []
    if len(metrics) > 0:
        metrics, metric_kwargs = get_metrics(metrics)
        scores = []
        output['scores'] = scores
        for metric_name, metric in metrics.items():
            scores.append({
                'metric': metric_name,
                'error': 'Metric Timeout',
            })
            output['scores'] = scores  # re-inject list to multiprocessing output

            error = None
            score = None
            normalized_score = None
            start = datetime.utcnow()
            try:
                LOGGER.info('Computing %s on dataset %s', metric_name, dataset_name)
                metric_args = (real_data, synthetic_data, metadata)
                score = metric.compute(*metric_args, **metric_kwargs.get(metric_name, {}))
                normalized_score = metric.normalize(score)
            except Exception:
                LOGGER.exception(
                    'Metric %s failed on dataset %s. Skipping.', metric_name, dataset_name)
                _, error = format_exception()

            scores[-1].update({
                'score': score,
                'normalized_score': normalized_score,
                'error': error,
                'metric_time': (datetime.utcnow() - start).total_seconds()
            })
            output['scores'] = scores  # re-inject list to multiprocessing output

    if compute_quality_score:
        start = datetime.utcnow()
        quality_report = SingleTableQualityReport()

        quality_report.generate(real_data, synthetic_data, metadata, verbose=False)
        output['quality_score_time'] = (datetime.utcnow() - start).total_seconds()
        output['quality_score'] = quality_report.get_score()


def compute_score(synthetic_data, synthesizer_name, data, metadata, metrics, output=None,
                  compute_quality_score=False, dataset_name=None):
    if output is None:
        output = {}

    output['timeout'] = True  # To be deleted if there is no error
    output['error'] = 'Load Timeout'  # To be deleted if there is no error
    try:

        del output['error']  # No error so far. _compute_scores tracks its own errors by metric
        _compute_scores(
            metrics,
            data,
            synthetic_data,
            metadata,
            output,
            compute_quality_score,
            dataset_name
        )

        output['timeout'] = False  # There was no timeout

    except Exception:
        LOGGER.exception('Error running %s on dataset %s;', synthesizer_name, dataset_name)

        exception, error = format_exception()
        output['exception'] = exception
        output['error'] = error
        output['timeout'] = False  # There was no timeout

    finally:
        LOGGER.info(
            'Finished %s on dataset %s; %s', synthesizer_name, dataset_name, used_memory())

    return output


def _score_with_timeout(timeout, synthesizer_name, data, metadata, metrics,
                        compute_quality_score=False, modality=None, dataset_name=None, output=None):
    with multiprocessing.Manager() as manager:
        output = manager.dict()
        process = multiprocessing.Process(
            target=compute_score,
            args=(
                synthesizer_name,
                data,
                metadata,
                metrics,
                output,
                compute_quality_score,
                modality,
                dataset_name
            ),
        )

        process.start()
        process.join(timeout)
        process.terminate()

        output = dict(output)
        if output.get('timeout'):
            LOGGER.error('Timeout running %s on dataset %s;', synthesizer_name['name'], dataset_name)

        return output


def _format_output(output, name, dataset_name, compute_quality_score, cache_dir):
    evaluate_time = None
    if 'scores' in output or 'quality_score_time' in output:
        evaluate_time = output.get('quality_score_time', 0)

    for score in output.get('scores', []):
        if score['metric'] == 'NewRowSynthesis':
            evaluate_time += score['metric_time']

    scores = pd.DataFrame({
        'Synthesizer': [name],
        'Dataset': [dataset_name],
        'Dataset_Size_MB': [output.get('dataset_size')],
        'Train_Time': [output.get('train_time')],
        'Peak_Memory_MB': [output.get('peak_memory')],
        'Synthesizer_Size_MB': [output.get('synthesizer_size')],
        'Sample_Time': [output.get('sample_time_ms')],
        'Evaluate_Time': [evaluate_time],
    })

    if compute_quality_score:
        scores.insert(len(scores.columns), 'Quality_Score', output.get('quality_score'))

    for score in output.get('scores', []):
        scores.insert(len(scores.columns), score['metric'], score['normalized_score'])

    if 'error' in output:
        scores['error'] = output['error']

    if cache_dir:
        cache_dir_name = str(cache_dir)
        base_path = f'{cache_dir_name}/{name}_{pathlib.Path(dataset_name).stem}'
        if scores is not None:
            write_csv(scores, f'{base_path}_scores.csv')
        if 'synthetic_data' in output:
            synthetic_data = compress_pickle.dumps(output['synthetic_data'], compression='gzip')
            write_file(synthetic_data, f'{base_path}.data.gz')
        if 'exception' in output:
            exception = output['exception'].encode('utf-8')
            write_file(exception, f'{base_path}_error.txt')

    return scores


def _run_job(synthesizer, data, metadata, metrics, cache_dir, timeout, compute_quality_score, dataset_name, detailed_results_folder):
    # Reset random seed
    np.random.seed()

    name = synthesizer['name']
    LOGGER.info('Evaluating %s on dataset %s with timeout %ss; %s',
                name, dataset_name, timeout, used_memory())


    LOGGER.info(
        'Running %s on dataset %s; %s',
        synthesizer['name'], dataset_name, used_memory()
    )
    synthetic_data_file_name=synthesizer['name']+'_'+Path(dataset_name).name
    synthetic_data, output=load_synthetic_dataset(os.path.join(detailed_results_folder, 'synthetic_data', synthetic_data_file_name))
    output['dataset_size'] = get_size_of(data) / N_BYTES_IN_MB
    output['error'] = 'Synthesizer Timeout'  # To be deleted if there is no error
    output['synthetic_data'] = synthetic_data

    LOGGER.info(
        'Scoring %s on dataset %s; %s',
        synthesizer['name'], dataset_name, used_memory()
    )
    try:
        if timeout:
            output = _score_with_timeout(
                timeout=timeout,
                synthesizer_name=synthesizer["name"],
                data=data,
                metadata=metadata,
                metrics=metrics,
                compute_quality_score=compute_quality_score,
                dataset_name=dataset_name,
                output=output
            )
        else:
            output = compute_score(
                synthetic_data=synthetic_data,
                synthesizer_name=synthesizer["name"],
                data=data,
                metadata=metadata,
                metrics=metrics,
                compute_quality_score=compute_quality_score,
                dataset_name=dataset_name,
                output=output
            )
    except Exception as error:
        output['exception'] = error

    scores = _format_output(output, name, dataset_name, compute_quality_score, cache_dir)

    return scores


def _get_empty_dataframe(compute_quality_score, sdmetrics):
    warnings.warn('No datasets/synthesizers_dict found.')

    scores = pd.DataFrame({
        'Synthesizer': [],
        'Dataset': [],
        'Dataset_Size_MB': [],
        'Train_Time': [],
        'Peak_Memory_MB': [],
        'Synthesizer_Size_MB': [],
        'Sample_Time': [],
        'Evaluate_Time': [],
    })

    if compute_quality_score:
        scores['Quality_Score'] = []
    if sdmetrics:
        for metric in sdmetrics:
            scores[metric[0]] = []

    return scores


def run(synthesizers=DEFAULT_SYNTHESIZERS, custom_synthesizers=None,
        sdv_datasets=DEFAULT_DATASETS, additional_datasets_folder=None,compute_quality_score=True,
        sdmetrics=DEFAULT_METRICS, timeout=None, output_filepath=None,
        detailed_results_folder=None):

    _validate_inputs(output_filepath, detailed_results_folder, synthesizers, custom_synthesizers)

    _create_results_directory(detailed_results_folder)

    scores = _run_all_scores(sdv_datasets, additional_datasets_folder, sdmetrics,
        detailed_results_folder, timeout, compute_quality_score, synthesizers, custom_synthesizers)


    if not scores:
        raise Exception('No valid Dataset/Synthesizer combination given.')


    scores = pd.concat(scores, ignore_index=True)
    if output_filepath:
        write_csv(scores, output_filepath)

    return scores
