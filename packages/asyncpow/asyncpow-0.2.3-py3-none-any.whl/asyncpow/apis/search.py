"""
AsyncPOW - https://github.com/totaldebug/asyncpow

Copyright (c) 2024 Steven Marks, Total Debug

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from aiohttp import ClientSession
from yarl import URL

from asyncpow.models.search import (
    DiscoverTrendingModel,
    DiscoverWatchlistModel,
    MovieResultModel,
    PersonResultModel,
    TvResultModel,
)
from asyncpow.utils.http import request


class Discover:
    """
    Class to interact with discover-related endpoints.

    Initialize the Discover object with the base URL, API key, and session.
    """

    def __init__(self, base_url: URL, api_key: str, session: ClientSession) -> None:
        """Initialize the SearchAPI object with the base URL, API key, and session.

        Args:
            base_url (str): The base URL for the media API.
            api_key (str): The API key for authentication.
            session (ClientSession): HTTP Session

        Returns:
            None
        """
        self.discover_url = base_url.joinpath("discover")
        self.api_key = api_key
        self.session = session

    async def async_get_trending(
        self, raw_response: bool = False, page: int = 1, lang: str = "en"
    ) -> dict | DiscoverTrendingModel:
        """
        Get trending items based on specified page and language.

        Args:
            raw_response (bool): Flag to determine whether to return the raw response (True) or an object (False). Default is False.
            page (int): The page number for trending items (default is 1).
            lang (str): The language for the trending items (default is "en").

        Returns:
            dict | DiscoverTrendingModel: The model object containing trending items.
        """

        url = self.discover_url.joinpath("trending").with_query({"page": page, "language": lang})
        headers = {"X-Api-Key": self.api_key}
        response = await request(self.session, url, headers=headers)
        if raw_response:
            return response
        trending_model = DiscoverTrendingModel(
            page=response["page"],
            totalPages=response["totalPages"],
            totalResults=response["totalResults"],
            results=[],
        )

        for item_data in response["results"]:
            media_type = item_data.get("mediaType")
            if item_model := {
                "tv": TvResultModel,
                "movie": MovieResultModel,
                "person": PersonResultModel,
            }.get(media_type, None):
                trending_model.results.append(item_model(**item_data))

        return trending_model

    async def async_get_watchlist(
        self, raw_response: bool = False, page: int = 1
    ) -> dict | DiscoverWatchlistModel:
        """
        Get the watchlist items based on the specified page.

        Args:
            raw_response (bool): Flag to determine whether to return the raw response (True) or an object (False). Default is False.
            page (int): The page number for watchlist items (default is 1).

        Returns:
            dict | DiscoverWatchlistModel: The model object containing watchlist items.
        """
        url = self.discover_url.joinpath("watchlist").with_query({"page": page})
        headers = {"X-Api-Key": self.api_key}
        response = await request(self.session, url, headers=headers)
        return response if raw_response else DiscoverWatchlistModel(**response)
