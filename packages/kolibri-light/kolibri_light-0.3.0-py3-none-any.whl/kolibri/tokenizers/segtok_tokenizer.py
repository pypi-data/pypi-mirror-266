import logging
import sys
from abc import ABC, abstractmethod
from typing import Callable, List
from kolibri.tokenizers.tokenizer import Tokenizer
from segtok.segmenter import split_single
from segtok.tokenizer import split_contractions, word_tokenizer


class SegtokTokenizer(Tokenizer):
    """Tokenizer using segtok, a third party library dedicated to rules-based Indo-European languages.

    For further details see: https://github.com/fnl/segtok
    """

    def __init__(self) -> None:
        super().__init__()

    def tokenize(self, text: str) -> List[str]:
        return SegtokTokenizer.run_tokenize(text)

    @staticmethod
    def run_tokenize(text: str) -> List[str]:
        words: List[str] = []

        sentences = split_single(text)
        for sentence in sentences:
            contractions = split_contractions(word_tokenizer(sentence))
            words.extend(contractions)

        words = list(filter(None, words))

        return words