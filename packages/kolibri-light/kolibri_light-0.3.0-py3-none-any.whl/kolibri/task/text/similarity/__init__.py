from kolibri.task.text.similarity.arxiv import ArxivSimilarity
from kolibri.task.text.similarity.azure_cognitive_search import AzureCognitiveSearchSimilarity
from kolibri.task.text.similarity.chatgpt_plugin_retriever import ChatGPTPluginSimilarity
from kolibri.task.text.similarity.contextual_compression import ContextualCompressionSimilarity
from kolibri.task.text.similarity.databerry import DataberrySimilarity
from kolibri.task.text.similarity.docarray import DocArraySimilarity
from kolibri.task.text.similarity.elastic_search_bm25 import ElasticSearchBM25Similarity
from kolibri.task.text.similarity.kendra import AmazonKendraSimilarity
from kolibri.task.text.similarity.knn import KNNSimilarity
from kolibri.task.text.similarity.llama_index import (
    LlamaIndexGraphSimilarity,
    LlamaIndexSimilarity,
)
from kolibri.task.text.similarity.merger_retriever import MergerSimilarity
from kolibri.task.text.similarity.metal import MetalSimilarity
from kolibri.task.text.similarity.milvus import MilvusSimilarity
from kolibri.task.text.similarity.pinecone_hybrid_search import PineconeHybridSearchSimilarity
from kolibri.task.text.similarity.pupmed import PubMedSimilarity
from kolibri.task.text.similarity.remote_retriever import RemoteLangChainSimilarity
from kolibri.task.text.similarity.svm import SVMSimilarity
from kolibri.task.text.similarity.tfidf import TFIDFSimilarity
from kolibri.task.text.similarity.time_weighted_retriever import (
    TimeWeightedVectorStoreSimilarity,
)
from kolibri.task.text.similarity.vespa_retriever import VespaSimilarity
from kolibri.task.text.similarity.weaviate_hybrid_search import WeaviateHybridSearchSimilarity
from kolibri.task.text.similarity.wikipedia import WikipediaSimilarity
from kolibri.task.text.similarity.zep import ZepSimilarity
from kolibri.task.text.similarity.zilliz import ZillizSimilarity

__all__ = [
    "AmazonKendraSimilarity",
    "ArxivSimilarity",
    "AzureCognitiveSearchSimilarity",
    "ChatGPTPluginSimilarity",
    "ContextualCompressionSimilarity",
    "DataberrySimilarity",
    "ElasticSearchBM25Similarity",
    "KNNSimilarity",
    "LlamaIndexGraphSimilarity",
    "LlamaIndexSimilarity",
    "MergerSimilarity",
    "MetalSimilarity",
    "MilvusSimilarity",
    "PineconeHybridSearchSimilarity",
    "PubMedSimilarity",
    "RemoteLangChainSimilarity",
    "SVMSimilarity",
    "TFIDFSimilarity",
    "TimeWeightedVectorStoreSimilarity",
    "VespaSimilarity",
    "WeaviateHybridSearchSimilarity",
    "WikipediaSimilarity",
    "ZepSimilarity",
    "ZillizSimilarity",
    "DocArraySimilarity",
]
