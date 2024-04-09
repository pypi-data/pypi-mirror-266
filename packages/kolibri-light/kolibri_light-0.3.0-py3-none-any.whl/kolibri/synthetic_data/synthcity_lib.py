
from synthpop.method import CART_METHOD
from kolibri.synthetic_data.base import BaseSingleTableSynthesizer
from synthcity.plugins import Plugins


class SynthcityTVAESynthesizer(BaseSingleTableSynthesizer):
    """Model wrapping ``TVAE`` model.

    Args:
        metadata (sdv.metadata.SingleTableMetadata):
            Single table metadata representing the data that this synthesizer_name will be used for.
        enforce_min_max_values (bool):
            Specify whether or not to clip the data returned by ``reverse_transform`` of
            the numerical transformer, ``FloatFormatter``, to the min and max values seen
            during ``fit``. Defaults to ``True``.
        enforce_rounding (bool):
            Define rounding scheme for ``numerical`` columns. If ``True``, the data returned
            by ``reverse_transform`` will be rounded as in the original data. Defaults to ``True``.
        embedding_dim (int):
            Size of the random sample passed to the Generator. Defaults to 128.
        compress_dims (tuple or list of ints):
            Size of each hidden layer in the encoder. Defaults to (128, 128).
        decompress_dims (tuple or list of ints):
           Size of each hidden layer in the decoder. Defaults to (128, 128).
        l2scale (int):
            Regularization term. Defaults to 1e-5.
        batch_size (int):
            Number of data samples to process in each step.
        epochs (int):
            Number of training epochs. Defaults to 300.
        loss_factor (int):
            Multiplier for the reconstruction error. Defaults to 2.
        cuda (bool or str):
            If ``True``, use CUDA. If a ``str``, use the indicated device.
            If ``False``, do not use cuda at all.
    """

    _model_sdtype_transformers = {'categorical': None}

    def __init__(self, metadata, enforce_min_max_values=True, enforce_rounding=True):

        super().__init__(
            metadata=metadata,
            enforce_min_max_values=enforce_min_max_values,
            enforce_rounding=enforce_rounding
        )

    def fit(self, processed_data):
        """Fit the model to the table.

        Args:
            processed_data (pandas.DataFrame):
                Data to be learned.
        """
        self._model = Plugins().get("tvae")

        self._model.fit(processed_data)


    def sample(self, num_rows, conditions=None):
        """Sample the indicated number of rows from the model.

        Args:
            num_rows (int):
                Amount of rows to sample.
            conditions (dict):
                If specified, this dictionary maps column names to the column
                value. Then, this method generates ``num_rows`` samples, all of
                which are conditioned on the given variables.

        Returns:
            pandas.DataFrame:
                Sampled data.
        """
        return self._model.generate(num_rows)


class SynthcityBNSynthesizer(BaseSingleTableSynthesizer):
    """Model wrapping ``Synthpop`` model.

    Args:
        metadata (sdv.metadata.TableMetadata):
            Single table metadata representing the data that this synthesizer_name will be used for.
        enforce_min_max_values (bool):
            Specify whether or not to clip the data returned by ``reverse_transform`` of
            the numerical transformer, ``FloatFormatter``, to the min and max values seen
            during ``fit``. Defaults to ``True``.
        enforce_rounding (bool):
            Define rounding scheme for ``numerical`` columns. If ``True``, the data returned
            by ``reverse_transform`` will be rounded as in the original data. Defaults to ``True``.
        locales (list or str):
            The default locale(s) to use for AnonymizedFaker transformers. Defaults to ``None``.

    """

    _model_sdtype_transformers = {'categorical': None}

    def __init__(self, metadata, enforce_min_max_values=True, enforce_rounding=True, locales=None):

        super().__init__(
            metadata=metadata,
            enforce_min_max_values=enforce_min_max_values,
            enforce_rounding=enforce_rounding,
            locales=locales
        )
        self._model = self._model = Plugins().get("bayesian_network")

    def fit(self, processed_data, epochs=None):
        """Fit the model to the table.

        Args:
            processed_data (pandas.DataFrame):
                Data to be learned.
        """
        self._model.fit(processed_data)
    def sample(self, num_rows):
        """Sample the indicated number of rows from the model.

        Args:
            num_rows (int):
                Amount of rows to sample.
            conditions (dict):
                If specified, this dictionary maps column names to the column
                value. Then, this method generates ``num_rows`` samples, all of
                which are conditioned on the given variables.

        Returns:
            pandas.DataFrame:
                Sampled data.
        """
        return self._model.generate(num_rows)



class SynthcityAdsGanSynthesizer(BaseSingleTableSynthesizer):
    """Model wrapping ``Synthpop`` model.

    Args:
        metadata (sdv.metadata.TableMetadata):
            Single table metadata representing the data that this synthesizer_name will be used for.
        enforce_min_max_values (bool):
            Specify whether or not to clip the data returned by ``reverse_transform`` of
            the numerical transformer, ``FloatFormatter``, to the min and max values seen
            during ``fit``. Defaults to ``True``.
        enforce_rounding (bool):
            Define rounding scheme for ``numerical`` columns. If ``True``, the data returned
            by ``reverse_transform`` will be rounded as in the original data. Defaults to ``True``.
        locales (list or str):
            The default locale(s) to use for AnonymizedFaker transformers. Defaults to ``None``.

    """

    _model_sdtype_transformers = {'categorical': None}

    def __init__(self, metadata, enforce_min_max_values=True, enforce_rounding=True, locales=None):

        super().__init__(
            metadata=metadata,
            enforce_min_max_values=enforce_min_max_values,
            enforce_rounding=enforce_rounding,
            locales=locales
        )
        self._model = self._model = Plugins().get("adsgan")

    def fit(self, processed_data, epochs=None):
        """Fit the model to the table.

        Args:
            processed_data (pandas.DataFrame):
                Data to be learned.
        """
        self._model.fit(processed_data)
    def sample(self, num_rows):
        """Sample the indicated number of rows from the model.

        Args:
            num_rows (int):
                Amount of rows to sample.
            conditions (dict):
                If specified, this dictionary maps column names to the column
                value. Then, this method generates ``num_rows`` samples, all of
                which are conditioned on the given variables.

        Returns:
            pandas.DataFrame:
                Sampled data.
        """
        return self._model.generate(num_rows)