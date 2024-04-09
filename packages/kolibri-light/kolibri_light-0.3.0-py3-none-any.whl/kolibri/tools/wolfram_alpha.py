"""Tool for the Wolfram Alpha API."""

from typing import Optional


from kolibri.utils.wrappers import WolframAlphaAPIWrapper


class WolframAlphaQueryRun():
    """Tool that adds the capability to query using the Wolfram Alpha SDK."""

    name = "wolfram_alpha"
    description = (
        "A wrapper around Wolfram Alpha. "
        "Useful for when you need to answer questions about Math, "
        "Science, Technology, Culture, Society and Everyday Life. "
        "Input should be a search query."
    )
    api_wrapper: WolframAlphaAPIWrapper

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the WolframAlpha tool."""
        return self.api_wrapper.run(query)
