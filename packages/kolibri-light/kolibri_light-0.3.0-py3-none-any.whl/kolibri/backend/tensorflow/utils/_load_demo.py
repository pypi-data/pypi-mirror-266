"""
Module that provides a method for loading an external dataset, for testing.
"""
import pandas as pd


def load_demo():
    """Loads an external dataset, for testing purposes.

    Returns
    -------
    tuple(pandas.DataFrame, list[str])
        DataFrame of the loaded CSV file, and a list with the corresponding
        discrete variables.

    Examples
    --------


    """
    demo_url = 'http://ctgan-demo.s3.amazonaws.com/census.csv.gz'
    discrete_columns = [
        'workclass',
        'education',
        'marital-status',
        'occupation',
        'relationship',
        'race',
        'sex',
        'native-country',
        'income'
    ]
    return pd.read_csv(demo_url, compression='gzip'), discrete_columns
