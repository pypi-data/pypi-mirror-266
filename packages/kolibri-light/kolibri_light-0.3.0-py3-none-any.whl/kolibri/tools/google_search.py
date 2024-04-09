"""Tool for the Google search API."""

from typing import Optional

from kolibri.utils.wrappers import GoogleSearchAPIWrapper


class GoogleSearch():
    """Tool that adds the capability to query the Google search API."""

    name = "google_search"
    description = (
        "A wrapper around Google Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: GoogleSearchAPIWrapper

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)


class GoogleSearchResults():
    """Tool that has capability to query the Google Search API and get back json."""

    name = "Google Search Results JSON"
    description = (
        "A wrapper around Google Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. Output is a JSON array of the query results"
    )
    num_results: int = 4
    api_wrapper: GoogleSearchAPIWrapper

    def _run(
        self,
        query: str,

    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.results(query, self.num_results))
