"""Wrappers on top of docstores."""
from kolibri.vectordb.docstore.arbitrary_fn import DocstoreFn
from kolibri.vectordb.docstore.in_memory import InMemoryDocstore
from kolibri.vectordb.docstore.wikipedia import Wikipedia

__all__ = ["DocstoreFn", "InMemoryDocstore", "Wikipedia"]
