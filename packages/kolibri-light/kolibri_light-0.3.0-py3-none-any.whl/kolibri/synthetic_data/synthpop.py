
from synthpop.method import CART_METHOD
from kolibri.synthetic_data.base import BaseSingleTableSynthesizer
from synthpop import Synthpop




class SynthpopSynthesizer(BaseSingleTableSynthesizer):
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

    def __init__(self, metadata, enforce_min_max_values=True, enforce_rounding=True, locales=None,
                 method=None,
                 visit_sequence=None,

                 proper=False,
                 cont_na=None,
                 smoothing=False,
                 default_method=CART_METHOD,
                 numtocat=None,
                 catgroups=None,
                 seed=None):

        super().__init__(
            metadata=metadata,
            enforce_min_max_values=enforce_min_max_values,
            enforce_rounding=enforce_rounding,
            locales=locales
        )
        self._model = Synthpop(method=method, visit_sequence=visit_sequence, proper=proper, cont_na=cont_na,
                             smoothing=smoothing, default_method=default_method, numtocat=numtocat,
                             catgroups=catgroups, seed=seed)

    def fit(self, processed_data, epochs=None):
        """Fit the model to the table.

        Args:
            processed_data (pandas.DataFrame):
                Data to be learned.
        """
        from kolibri.synthetic_data.metadata import TableMetadata
        metadata=TableMetadata()
        metadata.detect_from_dataframe(data=processed_data, detailed=True)
        dtypes=self._flatten_dict(metadata.to_dict()['columns'])
        self._model.fit(processed_data.astype(dtypes), dtypes)

    def _flatten_dict(self,d):
        for key, value in d.items():
            if isinstance(value, dict) and len(value) == 1:
                d[key] = next(iter(value.values()))
        return d
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

