"""Tool for the OpenWeatherMap API."""

from typing import Optional

from pydantic import Field



from kolibri.utils.wrappers import OpenWeatherMapAPIWrapper


class OpenWeatherMapQueryRun():
    """Tool that adds the capability to query using the OpenWeatherMap API."""

    api_wrapper: OpenWeatherMapAPIWrapper = Field(
        default_factory=OpenWeatherMapAPIWrapper
    )

    name = "OpenWeatherMap"
    description = (
        "A wrapper around OpenWeatherMap API. "
        "Useful for fetching current weather information for a specified location. "
        "Input should be a location string (e.g. London,GB)."
    )

    def _run(
        self, location: str,
    ) -> str:
        """Use the OpenWeatherMap tool."""
        return self.api_wrapper.run(location)

