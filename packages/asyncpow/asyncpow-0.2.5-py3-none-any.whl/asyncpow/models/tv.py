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

from asyncpow.models.common import (
    CreditModel,
    ExternalIdsModel,
    GenreModel,
    KeywordModel,
    ProductionCompanyModel,
    ProductionCountryModel,
    SpokenLanguagesModelTv,
    WatchProviderModel,
)


class EpisodeModel(BaseModel):
    """TV Episode model"""

    id: int
    name: str
    airDate: str | None
    episodeNumber: int
    overview: str
    productionCode: str
    seasonNumber: int
    showId: int
    stillPath: str | None
    voteAverage: float
    voteCount: int | None = None


class SeasonModel(BaseModel):
    """Model for TV Seasons"""

    id: int
    airDate: str | None = None
    episodeCount: int
    name: str
    overview: str
    posterPath: str | None = None
    seasonNumber: int


class CreatedByModel(BaseModel):
    """Model for Created by"""

    id: int
    name: str
    gender: int
    profilePath: str | None = None


class TvDetailsModel(BaseModel):
    """TV Details model"""

    id: int
    backdropPath: str
    posterPath: str
    contentRatings: dict
    createdBy: list[CreatedByModel]
    episodeRunTime: list[int]
    firstAirDate: str
    genres: list[GenreModel]
    homepage: str
    inProduction: bool
    languages: list[str]
    lastAirDate: str | None = None
    lastEpisodeToAir: EpisodeModel | None = None
    name: str
    nextEpisodeToAir: EpisodeModel | None = None
    networks: list[ProductionCompanyModel]
    numberOfEpisodes: int
    numberOfSeasons: int
    originCountry: list[str]
    originalLanguage: str
    originalName: str
    overview: str
    popularity: float
    productionCompanies: list[ProductionCompanyModel]
    productionCountries: list[ProductionCountryModel]
    spokenLanguages: list[SpokenLanguagesModelTv]
    seasons: list[SeasonModel]
    status: str
    tagline: str
    type: str
    voteAverage: float
    voteCount: int
    credits: CreditModel
    externalIds: ExternalIdsModel
    keywords: list[KeywordModel]
    watchProviders: list[WatchProviderModel]
