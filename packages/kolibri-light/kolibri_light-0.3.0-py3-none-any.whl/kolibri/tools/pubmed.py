"""Tool for the Pubmed API."""

from typing import Optional

from pydantic import Field

from kolibri.utils.wrappers import PubMedAPIWrapper


class PubmedQueryRun():
    """Tool that adds the capability to search using the PubMed API."""

    name = "PubMed"
    description = (
        "A wrapper around PubMed.org "
        "Useful for when you need to answer questions about Physics, Mathematics, "
        "Computer Science, Quantitative Biology, Quantitative Finance, Statistics, "
        "Electrical Engineering, and Economics "
        "from scientific articles on PubMed.org. "
        "Input should be a search query."
    )
    api_wrapper: PubMedAPIWrapper = Field(default_factory=PubMedAPIWrapper)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the Arxiv tool."""
        return self.api_wrapper.run(query)

