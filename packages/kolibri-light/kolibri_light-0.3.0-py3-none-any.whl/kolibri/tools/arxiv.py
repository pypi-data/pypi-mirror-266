"""Tool for the Arxiv API."""

from typing import Optional

from pydantic import Field

from kolibri.utils.wrappers import ArxivAPIWrapper


class ArxivQuery():
    """Tool that adds the capability to search using the Arxiv API."""

    name = "arxiv"
    description = (
        "A wrapper around Arxiv.org "
        "Useful for when you need to answer questions about Physics, Mathematics, "
        "Computer Science, Quantitative Biology, Quantitative Finance, Statistics, "
        "Electrical Engineering, and Economics "
        "from scientific articles on arxiv.org. "
        "Input should be a search query."
    )
    api_wrapper: ArxivAPIWrapper = Field(default_factory=ArxivAPIWrapper)

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the Arxiv tool."""
        return self.api_wrapper.run(query)
