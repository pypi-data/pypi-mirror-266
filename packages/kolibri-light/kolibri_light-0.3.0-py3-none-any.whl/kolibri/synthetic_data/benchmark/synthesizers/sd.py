"""SDV synthesizers_dict module."""
import abc
import logging
from kolibri.synthetic_data.benchmark.synthesizers.base import BaselineSynthesizer
from kolibri import synthetic_data
LOGGER = logging.getLogger(__name__)


class FastMLPreset(BaselineSynthesizer):
    """Model wrapping the ``FastMLPreset`` model."""

    _MODEL = None
    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        model = synthetic_data.SingleTablePreset(name='FAST_ML', metadata=metadata)
        model.fit(data)

        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        return synthesizer.sample(n_samples)

class SDVTabularSynthesizer(BaselineSynthesizer, abc.ABC):
    """Base class for single-table models."""

    _MODEL = None
    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata,  **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
        model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples)

class GaussianCopulaSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``GaussianCopulaSynthesizer`` model."""

    _MODEL = synthetic_data.GaussianCopulaSynthesizer



class CTGANSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CTGANSynthesizer`` model."""

    _MODEL = synthetic_data.CTGANSynthesizer


    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
 #       model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples)

class SynthpopSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CTGANSynthesizer`` model."""

    _MODEL = synthetic_data.SynthpopSynthesizer


    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
        model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples)

class SynthcityBNSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CTGANSynthesizer`` model."""

    _MODEL = synthetic_data.SynthcityBNSynthesizer


    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
 #       model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples).data

class SynthcityAdsGanSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CTGANSynthesizer`` model."""

    _MODEL = synthetic_data.SynthcityAdsGanSynthesizer


    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
 #       model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples).data

class SynthcityTVAESynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CTGANSynthesizer`` model."""

    _MODEL = synthetic_data.SynthcityTVAESynthesizer


    _MODEL_KWARGS = None

    def _get_trained_synthesizer(self, data, metadata, **model_kwargs):
        LOGGER.info('Fitting %s', self.__class__.__name__)
 #       model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples).data

class CopulaGANSynthesizer(SDVTabularSynthesizer):
    """Model wrapping the ``CopulaGANSynthesizer`` model."""

    def _get_trained_synthesizer(self, data, metadata,  **model_kwargs):
#        model_kwargs = self._MODEL_KWARGS.copy() if self._MODEL_KWARGS else {}
#        model_kwargs.setdefault('cuda', select_device())
        LOGGER.info('Fitting %s with kwargs %s', self.__class__.__name__, model_kwargs)
        model = self._MODEL(metadata=metadata, **model_kwargs)
        model.fit(data)
        return model

    def _sample_from_synthesizer(self, synthesizer, n_samples):
        LOGGER.info('Sampling %s', self.__class__.__name__)
        return synthesizer.sample(n_samples)


    _MODEL = synthetic_data.CopulaGANSynthesizer

