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

from asyncpow.models.tv import TvDetailsModel
from asyncpow.utils.http import request


class Tv:
    """
    Initialize the Tv object with the base URL and API key.
    """

    def __init__(self, base_url: URL, api_key: str, session: ClientSession) -> None:
        """
        Initialize the MovieAPI object with the base URL and API key.

        Args:
            base_url (str): The base URL for the media API.
            api_key (str): The API key for authentication.
            session (ClientSession): HTTP Session

        Returns:
            None
        """
        self.media_url = base_url.joinpath("tv")
        self.api_key = api_key
        self.session = session

    async def async_get_tv(
        self, tvId: int, lang: str = "en", raw_response: bool = False
    ) -> dict | TvDetailsModel:
        """
        Retrieves TV details by ID asynchronously.

        Args:
            tvId (int): The ID of the TV show.
            lang (str): The language for the response (default is "en").
            raw_response (bool): Flag to return raw response or TvDetailsModel (default is False).

        Returns:
            dict | TvDetailsModel: The raw response or TvDetailsModel object based on the raw_response flag.

        Examples:
            tv_details = await async_get_tv(12345, lang="en", raw_response=False)
        """
        params = {"language": lang}
        url = self.media_url.joinpath(str(tvId))

        headers = {"X-Api-Key": self.api_key}
        response = await request(self.session, url, params=params, headers=headers)
        return response if raw_response else TvDetailsModel(**response)
