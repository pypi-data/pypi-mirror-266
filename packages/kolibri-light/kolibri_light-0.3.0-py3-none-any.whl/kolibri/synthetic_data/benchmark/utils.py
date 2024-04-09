"""Random utils used by SDGym."""

import logging
import os
import subprocess
import sys
import traceback

import humanfriendly
import numpy as np
import pandas as pd
import psutil

from kolibri.synthetic_data.benchmark.synthesizers.base import BaselineSynthesizer

LOGGER = logging.getLogger(__name__)


def used_memory():
    """Get the memory used by this process nicely formatted."""
    process = psutil.Process(os.getpid())
    return humanfriendly.format_size(process.memory_info().rss)


def format_exception():
    """Format exceptions."""
    exception = traceback.format_exc()
    exc_type, exc_value, _ = sys.exc_info()
    error = traceback.format_exception_only(exc_type, exc_value)[0].strip()
    return exception, error


def get_synthesizers(synthesizers):
    """Get the dict of synthesizer_name name and object for each synthesizer_name.

    Args:
        synthesizers (list):
            An iterable of synthesizer_name classes and strings.

    Returns:
        dict[str, function]:
            Dict with the synthesizer_name name and object.

    Raises:
        TypeError:
            If neither a list is not passed.
    """
    synthesizers = [] if synthesizers is None else synthesizers
    if not isinstance(synthesizers, list):
        raise TypeError('`synthesizers_dict` must be a list.')

    synthesizers_dicts = []
    for synthesizer in synthesizers:
        synthesizer_kw={}
        if isinstance(synthesizer, str):
            baselines = BaselineSynthesizer.get_subclasses(include_parents=True)
            if synthesizer in baselines:
                LOGGER.info('Trying to import synthesizer_name by name.')
                synthesizer = baselines[synthesizer]
            else:
                raise Exception(f'Unknown synthesizer_name {synthesizer}') from None
        elif isinstance(synthesizer, dict):
            synthesizer_name = list(synthesizer.keys())[0]
            synthesizer_kw=synthesizer[synthesizer_name]
            baselines = BaselineSynthesizer.get_subclasses(include_parents=True)
            if synthesizer_name in baselines:
                LOGGER.info('Trying to import synthesizer_name by name.')
                synthesizer = baselines[synthesizer_name]
            else:
                raise Exception(f'Unknown synthesizer_name {synthesizer}') from None
        synthesizers_dicts.append({
            'name': getattr(synthesizer, '__name__', 'undefined'),
            'synthesizer_name': synthesizer,
            'kwargs': synthesizer_kw
        })

    return synthesizers_dicts


def get_size_of(obj, obj_ids=None):
    """Get the memory used by a given object in bytes.

    Args:
        obj (object):
            The object to get the size of.
        obj_ids (set):
            The ids of the objects that have already been evaluated.

    Returns:
        int:
            The size in bytes.
    """
    size = 0
    if obj_ids is None:
        obj_ids = set()

    obj_id = id(obj)
    if obj_id in obj_ids:
        return 0

    obj_ids.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size_of(v, obj_ids) for v in obj.values()])
    elif isinstance(obj, pd.DataFrame):
        size += obj.memory_usage(index=True).sum()
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size_of(i, obj_ids) for i in obj])
    else:
        size += sys.getsizeof(obj)

    return size


def get_duplicates(items):
    """Get any duplicate items in the given list.

    Args:
        items (list):
            The list of items to de-duplicate.

    Returns:
        set:
            The duplicate items.
    """
    seen = set()
    return {item for item in items if item in seen or seen.add(item)}


def get_num_gpus():
    """Get number of gpus.

    Returns:
        int:
            Number of gpus to use.
    """
    try:
        command = ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits']
        output = subprocess.run(command, stdout=subprocess.PIPE)
        return len(output.stdout.decode().split())

    except Exception:
        return 0



def bin_data(dt1, dt2, c = 10):
    dt1 = dt1.copy()
    dt2 = dt2.copy()
    # quantile binning of numerics
    num_cols = dt1.select_dtypes(include='number').columns
    for col in num_cols:
        # determine breaks based on `real_data`
        breaks = dt1[col].quantile(np.linspace(0, 1, c+1)).unique()
        dt1[col] = pd.cut(dt1[col], bins=breaks, include_lowest=True).astype(str)
        dt2_vals = pd.to_numeric(dt2[col], 'coerce')
        dt2_bins = pd.cut(dt2_vals, bins=breaks, include_lowest=True).astype(str)
        dt2_bins[dt2_vals < min(breaks)] = '_other_'
        dt2_bins[dt2_vals > max(breaks)] = '_other_'
        dt2[col] = dt2_bins
    # convert bools to categoricals
    bool_cols = dt1.select_dtypes(include=['bool'])
    for col in bool_cols:
        dt1[col] = dt1[col].astype('str')
        dt2[col] = dt2[col].astype('str')
    # top-C binning of categoricals
    cat_cols = dt1.select_dtypes(include=['object', 'category', 'string'])
    for col in cat_cols:
        # determine top values based on `real_data`
        top_vals = dt1[col].value_counts().head(c).index.tolist()
        dt1[col].replace(np.setdiff1d(dt1[col].unique().tolist(), top_vals), '_other_', inplace=True)
        dt2[col].replace(np.setdiff1d(dt2[col].unique().tolist(), top_vals), '_other_', inplace=True)
    return [dt1, dt2]
