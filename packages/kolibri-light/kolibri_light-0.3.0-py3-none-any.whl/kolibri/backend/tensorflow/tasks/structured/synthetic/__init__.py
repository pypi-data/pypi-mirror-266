"""
The :mod:`ctgan.synthesizer_name` module contains the definition of the CTGAN
Synthesizer - the "main" class for training a Conditional Tabular GAN, as well
as helper methods to control the execution of the training steps.

It contains the Tensorflow 2 implementation of the work published in
*Modeling Tabular data using Conditional GAN* :cite:`xu2019modeling`.
The original PyTorch implementation can be found in the authors'
"""

from ._synthesizer import CTGANSynthesizer
__all__ = [
    'CTGANSynthesizer'
]
