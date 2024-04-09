"""Module for parsing text files.."""
from typing import Iterator

from kolibri.data.parsers.base import BaseBlobParser
from kolibri.data.blob import Blob
from kolibri.data.document import Document


class TextParser(BaseBlobParser):
    """Parser for text blobs."""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""
        yield Document(page_content=blob.as_string(), metadata={"source": blob.source})
