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

from asyncpow.models.status import StatusAppDataModel, StatusModel
from asyncpow.utils.http import request


class Status:
    """
    Class to interact with status-related endpoints.

    Initialize the Status object with the base URL, API key, and session.
    """

    def __init__(self, base_url: URL, api_key: str, session: ClientSession) -> None:
        """
        Initialize the Status object with the base URL, API key, and session.

        Returns:
            None
        """

        self.base_url = base_url.joinpath("status")
        self.api_key = api_key
        self.session = session

    async def async_get_status(self, raw_response: bool = False) -> dict | StatusModel:
        """
        Summary:
            Asynchronously retrieves the status from the server.

        Args:
            raw_response (bool): Flag to determine whether to return the raw response (True) or an object (False). Default is False.

        Returns:
            dict | StatusModel: The status information as either a dictionary or a StatusModel object.
        """
        response = await request(self.session, self.base_url)
        return response if raw_response else StatusModel(**response)

    async def async_get_appdata(self, raw_response: bool = False) -> dict | StatusAppDataModel:
        """Retrieves the appdata from the server

        Args:
            raw_response (bool, optional): Flag to determine whether to return the raw response (True) or an object (False). Default is False.

        Returns:
            dict | StatusAppDataModel: The model object containing appdata items.
        """
        url = self.base_url.joinpath("appdata")
        response = await request(self.session, url)
        return response if raw_response else StatusAppDataModel(**response)
