
from itertools import chain
from logging import getLogger
from typing import List, Callable, Union, Tuple, Optional
from kolibri.tokenizers.sentence_tokenizer import split_text_to_sentences
from kolibri.registry import register
from kolibri.core.component import Component

logger = getLogger(__name__)


@register('DocumentChunker')
class DocumentChunker(Component):
    """Make chunks from a document or a list of documents. Don't tear up sentences if needed.

    Args:
        sentencize_fn: a function for sentence segmentation
        keep_sentences: whether to tear up sentences between chunks or not
        tokens_limit: a number of tokens in a single chunk (usually this number corresponds to the squad model limit)
        flatten_result: whether to flatten the resulting list of lists of chunks
        paragraphs: whether to split document by paragrahs; if set to True, tokens_limit is ignored

    Attributes:
        keep_sentences: whether to tear up sentences between chunks or not
        tokens_limit: a number of tokens in a single chunk
        flatten_result: whether to flatten the resulting list of lists of chunks
        paragraphs: whether to split document by paragrahs; if set to True, tokens_limit is ignored

    """

    def __init__(self,  keep_sentences: bool = True, tokens_limit: int = 400,
                 flatten_result: bool = False, paragraphs: bool = False, number_of_paragraphs: int = -1, *args,
                 **kwargs) -> None:
        super().__init__()
        self.keep_sentences = keep_sentences
        self.tokens_limit = tokens_limit
        self.flatten_result = flatten_result
        self.paragraphs = paragraphs
        self.number_of_paragraphs = number_of_paragraphs


    def fit(self, X, y=None):
        return self(X)

    def __call__(self, batch_docs: List[Union[str, List[str]]],
                 batch_docs_ids: Optional[List[Union[str, List[str]]]] = None) -> \
            Union[Tuple[Union[List[str], List[List[str]]], Union[List[str], List[List[str]]]],
                  Union[List[str], List[List[str]]]]:
        """Make chunks from a batch of documents. There can be several documents in each batch.
        Args:
            batch_docs: a batch of documents / a batch of lists of documents
            batch_docs_ids (optional) : a batch of documents ids / a batch of lists of documents ids
        Returns:
            chunks of docs, flattened or not and
            chunks of docs ids, flattened or not if batch_docs_ids were passed
        """

        result = []
        result_ids = []

        empty_docs_ids_flag = False

        if not batch_docs_ids:
            empty_docs_ids_flag = True

        if empty_docs_ids_flag:
            batch_docs_ids = [[[] for j in i] for i in batch_docs]

        for ids, docs in zip(batch_docs_ids, batch_docs):
            batch_chunks = []
            batch_chunks_ids = []
            if isinstance(docs, str):
                docs = [docs]
                ids = [ids]

            for id, doc in zip(ids, docs):
                if self.paragraphs:
                    split_doc = doc.split('\n\n')
                    split_doc = [sd.strip() for sd in split_doc]
                    split_doc = list(filter(lambda x: len(x) > 40, split_doc))
                    if self.number_of_paragraphs != -1:
                        split_doc = split_doc[:self.number_of_paragraphs]
                    batch_chunks.append(split_doc)
                    batch_chunks_ids.append([id] * len(split_doc))
                else:
                    doc_chunks = []
                    if self.keep_sentences:
                        sentences = split_text_to_sentences(doc)
                        n_tokens = 0
                        keep = []
                        for s in sentences:
                            n_tokens += len(s.split())
                            if n_tokens > self.tokens_limit:
                                if keep:
                                    doc_chunks.append(' '.join(keep))
                                    n_tokens = 0
                                    keep.clear()
                            keep.append(s)
                        if keep:
                            doc_chunks.append(' '.join(keep))
                        batch_chunks.append(doc_chunks)
                        batch_chunks_ids.append([id] * len(doc_chunks))
                    else:
                        split_doc = doc.split()
                        doc_chunks = [split_doc[i:i + self.tokens_limit] for i in
                                      range(0, len(split_doc), self.tokens_limit)]
                        batch_chunks.append(doc_chunks)
                        batch_chunks_ids.append([id] * len(doc_chunks))
            result.append(batch_chunks)
            result_ids.append(batch_chunks_ids)

        if self.flatten_result:
            if isinstance(result[0][0], list):
                for i in range(len(result)):
                    flattened = list(chain.from_iterable(result[i]))
                    flattened_ids = list(chain.from_iterable(result_ids[i]))
                    result[i] = flattened
                    result_ids[i] = flattened_ids

        if empty_docs_ids_flag:
            return result

        return result, result_ids
