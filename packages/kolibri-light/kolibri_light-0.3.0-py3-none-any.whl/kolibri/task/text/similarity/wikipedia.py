from typing import List

from kolibri.core.document import  Document
from kolibri.utils.wrappers import WikipediaAPIWrapper


class WikipediaSimilarity(WikipediaAPIWrapper):
    """
    It is effectively a wrapper for WikipediaAPIWrapper.
    It wraps load() to get_relevant_documents().
    It uses all WikipediaAPIWrapper arguments without any change.
    """

    def get_relevant_documents(self, query: str) -> List[Document]:
        return self.load(query=query)

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError
