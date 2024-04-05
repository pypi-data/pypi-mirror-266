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

from pydantic import BaseModel


class MovieResultModel(BaseModel):
    """
    Data class representing a movie search result.
    """

    id: int
    mediaType: str
    popularity: float
    posterPath: str
    backdropPath: str
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


class TvResultModel(BaseModel):
    """
    Data class representing a TV show search result.
    """

    id: int
    mediaType: str
    popularity: float
    posterPath: str
    backdropPath: str
    voteCount: int
    voteAverage: float
    genreIds: list[int]
    overview: str
    originalLanguage: str
    name: str
    originalName: str
    originCountry: list[str]
    firstAirDate: str


class PersonResultModel(BaseModel):
    """
    Data class representing a person search result.
    """

    id: int
    profilePath: str
    adult: bool
    mediaType: str
    knwonFor: list[MovieResultModel | TvResultModel]


class DiscoverTrendingModel(BaseModel):
    """
    Data class representing trending items in discovery.
    """

    page: int
    totalPages: int
    totalResults: int
    results: list[MovieResultModel | TvResultModel | PersonResultModel]


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
