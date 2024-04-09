""" lite package that contains model presets."""

from kolibri.synthetic_data.single_table import SingleTablePreset, GaussianCopulaSynthesizer
from kolibri.synthetic_data.copulagan import CopulaGANSynthesizer
from kolibri.synthetic_data.ctgan_synthesizer import CTGANSynthesizer
from kolibri.synthetic_data.synthpop import SynthpopSynthesizer
from kolibri.synthetic_data.synthcity_lib import SynthcityBNSynthesizer, SynthcityAdsGanSynthesizer, SynthcityTVAESynthesizer

__all__ = (
    'SingleTablePreset',
    'CTGANSynthesizer',
    'GaussianCopulaSynthesizer',
    'CopulaGANSynthesizer',
    'SynthpopSynthesizer',
    'SynthcityBNSynthesizer',
    'SynthcityAdsGanSynthesizer',
    'SynthcityTVAESynthesizer'

)
