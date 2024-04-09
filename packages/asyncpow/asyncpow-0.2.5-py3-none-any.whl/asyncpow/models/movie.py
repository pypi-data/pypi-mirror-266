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

from typing import Literal

from pydantic import BaseModel

from asyncpow.models.common import (
    CreditModel,
    ExternalIdsModel,
    GenreModel,
    KeywordModel,
    ProductionCompanyModel,
    ProductionCountryModel,
    SpokenLanguagesModelMovie,
    WatchProviderModel,
)


class RelatedVideoModel(BaseModel):
    """
    Data class representing a related video.
    """

    url: str
    key: str
    name: str
    size: int
    type: Literal[
        "Clip",
        "Teaser",
        "Trailer",
        "Featurette",
        "Opening Credits",
        "Behind the Scenes",
        "Bloopers",
    ]
    site: Literal["YouTube"]


class CollectionModel(BaseModel):
    """
    Data class representing a collection.
    """

    id: int
    name: str
    posterPath: str
    backdropPath: str


class RequestedByModel(BaseModel):
    """
    Data class representing the user who made the request.
    """

    id: int
    email: str
    username: str
    plexToken: str
    plexUsername: str
    userType: int
    permissions: int
    avatar: str
    createdAt: str
    updatedAt: str
    requestCount: int


class ModifiedByModel(BaseModel):
    """
    Data class representing the user who modified the item.
    """

    id: int
    email: str
    username: str
    plexToken: str
    plexUsername: str
    userType: int
    permissions: int
    avatar: str
    createdAt: str
    updatedAt: str
    requestCount: int


class RequestModel(BaseModel):
    """
    Data class representing a request.
    """

    id: int
    status: int
    media: str
    createdAt: str
    updatedAt: str
    requestedBy: RequestedByModel
    modifiedBy: ModifiedByModel
    is4k: bool
    serverId: int
    profileId: int
    rootFolder: str


class MediaInfoModel(BaseModel):
    """
    Data class representing media information.
    TODO: check this is used
    """

    id: int
    tmdbId: int
    tvdbId: int
    status: int
    requests: list[RequestModel]
    createdAt: str
    updatedAt: str


class MovieDetailsModel(BaseModel):
    """
    Data class representing a movie model.
    """

    id: int
    adult: bool
    backdropPath: str
    posterPath: str
    budget: int
    genres: list[GenreModel]
    homepage: str
    originalLanguage: str
    originalTitle: str
    overview: str
    popularity: float
    productionCompanies: list[ProductionCompanyModel]
    productionCountries: list[ProductionCountryModel]
    releaseDate: str
    releases: dict
    revenue: int
    runtime: int
    spokenLanguages: list[SpokenLanguagesModelMovie]
    status: str
    tagline: str
    title: str
    video: bool
    voteAverage: float
    voteCount: int
    externalIds: ExternalIdsModel
    watchProviders: list[WatchProviderModel]
    keywords: list[KeywordModel]
    relatedVideos: list[RelatedVideoModel]
    credits: CreditModel
    imdbId: str | None = None
    collection: CollectionModel | None = None
