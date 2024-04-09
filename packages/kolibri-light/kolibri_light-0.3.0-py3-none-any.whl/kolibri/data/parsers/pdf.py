"""Module contains common parsers for PDFs."""
from typing import Iterator

from kolibri.data.loaders.base import BaseBlobParser
from kolibri.data.blob import Blob
from kolibri.data.document import Document


class PyPDFParser(BaseBlobParser):
    """Loads a PDF with pypdf and chunks at character level."""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse the blob."""
        import pypdf

        with blob.as_bytes_io() as pdf_file_obj:
            pdf_reader = pypdf.PdfReader(pdf_file_obj)
            yield from [
                Document(
                    page_content=page.extract_text(),
                    metadata={"source": blob.source, "page": page_number},
                )
                for page_number, page in enumerate(pdf_reader.pages)
            ]
