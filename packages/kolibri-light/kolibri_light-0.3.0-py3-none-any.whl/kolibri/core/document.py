
from kolibri.utils.serializable import Serializable
from pydantic import Field


class Document(Serializable):
    """Interface for all documents."""

    page_content: str
    metadata: dict = Field(default_factory=dict)
