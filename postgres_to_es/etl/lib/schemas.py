"""Schemas to transform and validate data."""

from typing import List, Optional

from pydantic import BaseModel


class Person(BaseModel):
    """Person data schema."""

    id: str
    name: str


class Movie(BaseModel):
    """Movie data schema."""

    id: str
    imdb_rating: Optional[float]
    genre: List[str]
    title: str
    description: Optional[str]
    director: List[str]
    actors_names: List[str]
    writers_names: List[str]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]

    class Config:
        allow_population_by_field_name = True
