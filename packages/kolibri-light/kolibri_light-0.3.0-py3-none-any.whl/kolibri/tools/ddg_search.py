"""Tool for the DuckDuckGo search API."""

import warnings
from typing import Any, Optional

from pydantic import Field

from kolibri.utils.wrappers import DuckDuckGoSearchAPIWrapper


class DuckDuckGoSearch():
    """Tool that adds the capability to query the DuckDuckGo search API."""

    name = "duckduckgo_search"
    description = (
        "A wrapper around DuckDuckGo Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: DuckDuckGoSearchAPIWrapper = Field(
        default_factory=DuckDuckGoSearchAPIWrapper
    )

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)


class DuckDuckGoSearchResults():
    """Tool that queries the Duck Duck Go Search API and get back json."""

    name = "DuckDuckGo Results JSON"
    description = (
        "A wrapper around Duck Duck Go Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. Output is a JSON array of the query results"
    )
    num_results: int = 4
    api_wrapper: DuckDuckGoSearchAPIWrapper = Field(
        default_factory=DuckDuckGoSearchAPIWrapper
    )

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.results(query, self.num_results))

