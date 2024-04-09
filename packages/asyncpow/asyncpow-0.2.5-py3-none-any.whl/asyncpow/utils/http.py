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

import asyncio
import json
from typing import Any, Mapping, Optional

from aiohttp import ClientError, ClientSession, hdrs
import backoff
from yarl import URL

from asyncpow.exceptions import POWConnectionException, POWException, POWTimeoutException


@backoff.on_exception(backoff.expo, POWConnectionException, max_tries=5, logger=None)
async def request(
    session: ClientSession,
    url: URL,
    method: str = hdrs.METH_GET,
    request_timeout: int = 10,
    data: Any | None = None,
    json_data: dict[str, Any] | None = None,
    params: Mapping[str, str] | None = None,
    headers: Optional[dict] = None,
) -> Any:
    """Make an HTTP request with backoff and retry logic.


    Args:
        session (ClientSession): The aiohttp ClientSession to use for the request
        url (URL): The URL to sent the request to
        method (str, optional): The HTTP method to use fir the request. Defaults to hdrs.METH_GET.
        request_timeout (int, optional): Timeout for the request in seconds. Defaults to 10.
        data (Any | None, optional): data to include in the request. Defaults to None.
        json_data (dict[str, Any] | None, optional): JSON data to include in the request. Defaults to None.
        params (Mapping[str, str] | None, optional): parameters required for the request. Defaults to None.
        headers (Optional[dict], optional): headers required for the request. Defaults to None.

    Raises:
        POWTimeoutException: Request timeout error
        POWConnectionException: Connection issue error
        POWException: Generic exception

    Returns:
        Any: Response in JSON or text
    """
    if params:
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = str(value).lower()

    try:
        async with asyncio.timeout(request_timeout):
            response = await session.request(
                method,
                url,
                data=data,
                json=json_data,
                params=params,
                headers=headers,
            )
    except asyncio.TimeoutError as exception:
        msg = "Timeout occurred while connecting to Overseerr instance."
        raise POWTimeoutException(msg) from exception
    except ClientError as exception:
        msg = "Error occurred while communicating with Overseerr."
        raise POWConnectionException(msg) from exception

    content_type = response.headers.get("Content-Type", "")
    if response.status // 100 in [4, 5]:
        contents = await response.read()
        response.close()

        if content_type == "application/json":
            raise POWException(response.status, json.loads(contents.decode("utf8")))
        raise POWException(response.status, {"message": contents.decode("utf8")})

    if "application/json" in content_type:
        return await response.json()

    text = await response.text()
    return {"message": text}
