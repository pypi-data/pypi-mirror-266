"""Tool for the Bing search API."""

from typing import Optional

from kolibri.utils.wrappers import BingSearchAPIWrapper


class BingSearch():
    """Tool that adds the capability to query the Bing search API."""

    name = "bing_search"
    description = (
        "A wrapper around Bing Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: BingSearchAPIWrapper

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)



class BingSearchResults():
    """Tool that has capability to query the Bing Search API and get back json."""

    name = "Bing Search Results JSON"
    description = (
        "A wrapper around Bing Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. Output is a JSON array of the query results"
    )
    num_results: int = 4
    api_wrapper: BingSearchAPIWrapper

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.results(query, self.num_results))
