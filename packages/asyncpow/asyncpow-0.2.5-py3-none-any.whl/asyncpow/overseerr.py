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

import aiohttp
from cachetools import TTLCache
from yarl import URL

from asyncpow.apis.media import Media
from asyncpow.apis.movie import Movie
from asyncpow.apis.search import Discover
from asyncpow.apis.status import Status
from asyncpow.apis.tv import Tv
from asyncpow.const import API_URI

VERSION_CACHE: TTLCache[str, str | None] = TTLCache(maxsize=16, ttl=7200)


class Overseerr:
    """The Overseerr class provides convenient access to Overseerr's API.

    Instances of this class are the gateway to interacting with Overseerr's API through
    AsyncPOW. The canonical way to obtain an instance of this class is via:

    .. code-block:: python

        from asyncpow import overseerr

        async with Overseerr(
            host="OVERSEERR_HOST",
            api_key="OVERSEER_KEY",
            port=5055,
            tls=True,
            base_url="overseerr/",
        ) as api:
            # Inside the context, you can use the API wrapper as needed
            status = await api.status.get_status()
            print("Status:", status)

    """

    def __init__(
        self,
        host: str,
        api_key: str,
        port: int | None = None,
        tls: bool = True,
        base_path: str = "",
    ):
        """
        Initialize the Overseerr API client with the host, API key, and optional port, SSL, and base URL.

        Args:
            host (str): The host of the Overseerr instance.
            api_key (str): The API key for authentication.
            port (int, Optional): The port of the Overseerr instance (default is None).
            tls (bool): Flag indicating whether SSL is enabled (default is True).
            base_path (str): The base URL for the API (default is "").

        Returns:
            None
        """
        scheme = "https" if tls else "http"
        self.url = URL.build(
            scheme=scheme,
            host=host,
            port=port,
            path=base_path,
        ).joinpath(API_URI)
        self.api_key = api_key

        # Initialize a single instance of ClientSession
        self._session = aiohttp.ClientSession()
        # Initialize instances of API classes
        self.status = Status(self.url, self.api_key, self._session)
        self.discover = Discover(self.url, self.api_key, self._session)
        self.media = Media(self.url, self.api_key, self._session)
        self.movie = Movie(self.url, self.api_key, self._session)
        self.tv = Tv(self.url, self.api_key, self._session)

    async def __aenter__(self):
        """
        Enter method for asynchronous context manager.

        Returns:
            self
        """
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Exit method for asynchronous context manager.

        Args:
            exc_type: The exception type.
            exc: The exception instance.
            tb: The traceback.

        Returns:
            None

        Raises:
            Any exceptions raised during the session close operation.
        """

        # Close the session when exiting the context manager
        await self._session.close()
