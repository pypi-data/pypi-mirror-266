"""
The :mod:`ctgan.layers` module contains the definition of custom neural
networks layers, and helper methods to initialize their weights and bias.

For further details, please consult sections 4.4 of :cite:`xu2019modeling`.
"""

from .layer_utils import init_bounded
from .residual import ResidualLayer
from .gen_activation import GenActivation

# encoding: utf-8



# file: __init__.py
# time: 7:39

from typing import Dict, Any
from tensorflow import keras

from .conditional_random_field import KConditionalRandomField
from .behdanau_attention import BahdanauAttention  # type: ignore

L = keras.layers
L.BahdanauAttention = BahdanauAttention
L.KConditionalRandomField = KConditionalRandomField


def resigter_custom_layers(custom_objects: Dict[str, Any]) -> Dict[str, Any]:
    custom_objects['KConditionalRandomField'] = KConditionalRandomField
    custom_objects['BahdanauAttention'] = BahdanauAttention
    return custom_objects

__all__ = [
    'init_bounded',
    'ResidualLayer',
    'GenActivation'
]
