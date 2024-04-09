"""Base classes for synthesizers_dict."""

import logging
from kolibri.core.component import Component
from kolibri.synthetic_data.metadata import TableMetadata
import abc

LOGGER = logging.getLogger(__name__)


class BaselineSynthesizer(Component):
    """Base class for all the baselines."""
    @classmethod
    def get_baselines(cls):
        """Get baseline classes."""
        subclasses = cls.get_subclasses(include_parents=True)
        synthesizers = []
        for _, subclass in subclasses.items():
            if abc.ABC not in subclass.__bases__:
                synthesizers.append(subclass)

        return synthesizers

    def get_trained_synthesizer(self, data, metadata, **kwargs):
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
#        metadata_class = TableMetadata()
#        metadata = metadata_class.load_from_dict(metadata)
        return self._get_trained_synthesizer(data, metadata, **kwargs)

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
        return self._sample_from_synthesizer(synthesizer, n_samples)

    def _get_trained_synthesizer(self, data, metadata, **kwargs):
        raise NotImplementedError


    def _sample_from_synthesizer(self, synthesizer, n_samples):
        raise NotImplementedError