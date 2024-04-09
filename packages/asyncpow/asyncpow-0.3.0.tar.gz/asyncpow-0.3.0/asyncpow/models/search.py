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

from pydantic import BaseModel, validator

from asyncpow.exceptions import POWMediaTypeException
from asyncpow.models.common import MediaInfoModel


class MovieResultModel(BaseModel):
    """
    Data class representing a movie search result.
    """

    id: int
    mediaType: str
    popularity: float
    voteCount: int
    voteAverage: float
    genreIds: list[int]
    overview: str
    originalLanguage: str
    title: str
    originalTitle: str
    releaseDate: str
    adult: bool
    video: bool
    posterPath: str | None = None
    backdropPath: str | None = None
    mediaInfo: MediaInfoModel | None = None


class TvResultModel(BaseModel):
    """
    Data class representing a TV show search result.
    """

    id: int
    mediaType: str
    popularity: float
    voteCount: int
    voteAverage: float
    genreIds: list[int]
    overview: str
    originalLanguage: str
    name: str
    originalName: str
    originCountry: list[str]
    firstAirDate: str
    posterPath: str | None = None
    backdropPath: str | None = None
    mediaInfo: MediaInfoModel | None = None


class PersonResultModel(BaseModel):
    """
    Data class representing a person search result.
    """

    id: int
    name: str
    popularity: float
    adult: bool
    mediaType: str
    knownFor: list[MovieResultModel | TvResultModel]
    profilePath: str | None = None

    @validator("knownFor", pre=True)
    def validate_knownfor(cls, v):
        """
        Validate the 'knownFor' field by creating and returning a list of validated known for items.

        Args:
            v: The value to be validated.

        Returns:
            list: A list of validated known for items.

        Raises:
            POWMediaTypeException: If the media type is unsupported.

        Examples:
            validated_known_for = validate_knownfor(v)
        """

        validated_known_for = []
        for item in v:
            media_type = item.get("mediaType")
            if media_type == "movie":
                validated_known_for.append(MovieResultModel(**item))
            elif media_type == "tv":
                validated_known_for.append(TvResultModel(**item))
            else:
                raise POWMediaTypeException(f"Unsupported Media Type: {media_type}")
        return validated_known_for


class SearchResultModel(BaseModel):
    """
    Data class representing search items in search.
    """

    page: int
    totalPages: int
    totalResults: int
    results: list[MovieResultModel | TvResultModel | PersonResultModel]

    @validator("results", pre=True)
    def validate_results(cls, v):
        """
        Validate the 'results' field by creating and returning a list of validated result items.

        Args:
            v: The value to be validated.

        Returns:
            list: A list of validated result items.

        Raises:
            POWMediaTypeException: If the media type is unsupported.
        """

        validated_results = []
        for item in v:
            media_type = item.get("mediaType")
            if media_type == "movie":
                validated_results.append(MovieResultModel(**item))
            elif media_type == "tv":
                validated_results.append(TvResultModel(**item))
            elif media_type == "person":
                validated_results.append(PersonResultModel(**item))
            else:
                raise POWMediaTypeException(f"Unsupported Media Type: {media_type}")
        return validated_results


class WatchlistModel(BaseModel):
    """
    Data class representing an item in the watchlist.
    """

    ratingKey: str
    title: str
    mediaType: str
    tmdbId: int


class DiscoverWatchlistModel(BaseModel):
    """
    Data class representing watchlist items in discovery.
    """

    page: int
    totalPages: int
    totalResults: int
    results: list[WatchlistModel]
