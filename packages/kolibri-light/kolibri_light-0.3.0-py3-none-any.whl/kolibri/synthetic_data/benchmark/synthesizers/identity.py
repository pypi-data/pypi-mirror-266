"""DataIdentity module."""
import copy

from kolibri.synthetic_data.benchmark.synthesizers.base import BaselineSynthesizer


class DataIdentity(BaselineSynthesizer):
    """Trivial synthesizer_name.

    Returns the same exact data that is used to fit it.
    """

    def __init__(self):
        self._data = None

    def get_trained_synthesizer(self, data, metadata):
        """Get a synthesizer_name that has been trained on the provided data and metadata.

        Args:
            data (pandas.DataFrame):
                The data to train on.
            metadata (dict):
                The metadata dictionary.

        Returns:
            obj:
                The synthesizer_name object.
        """
        self._data = data
        return None

    def sample_from_synthesizer(self, synthesizer, n_samples):
        """Sample data from the provided synthesizer_name.

        Args:
            synthesizer (obj):
                The synthesizer_name object to sample data from.
            n_samples (int):
                The number of samples to create.

        Returns:
            pandas.DataFrame or dict:
                The sampled data. If single-table, should be a DataFrame. If multi-table,
                should be a dict mapping table name to DataFrame.
        """
        return copy.deepcopy(self._data)
