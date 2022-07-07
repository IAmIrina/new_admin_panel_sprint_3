"""Project settings."""
from typing import Set
from pydantic import BaseSettings, Field
from lib import es_index_schema


class PostgresSettings(BaseSettings):
    """Postgres connection settings."""
    host: str = Field('127.0.0.1', env='DB_HOST')
    port: str = Field(5432, env='DB_PORT')
    dbname: str = Field(env='DB_NAME')
    user: str = Field(env='DB_USER')
    password: str = Field(env='DB_PASSWORD')
    connect_timeout: int = 1


class ElasticsearchConnection(BaseSettings):
    """Elasticsearch connection settings."""
    hosts: str = Field('http://localhost:9200', env='ES_HOST')


class ElasticsearchSettings(BaseSettings):
    """Elasticsearch index settings."""
    connection: ElasticsearchConnection = ElasticsearchConnection()
    index: str = 'movies'
    index_schema: dict = es_index_schema.movies


class RedisSettings(BaseSettings):
    """Redis connection settings."""
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='DEFAULT_REDIS_PORT')
    password: str = Field(env='REDIS_PASSWORD')


class Cashe(BaseSettings):
    """Redis connection settings for every processor."""
    extractor: dict = {**RedisSettings().dict(), 'db': 1}
    enricher: dict = {**RedisSettings().dict(), 'db': 2}
    transformer: dict = {**RedisSettings().dict(), 'db': 3}
    loader: dict = {**RedisSettings().dict(), 'db': 4}


class Settings(BaseSettings):
    """Project settings."""

    postgres: PostgresSettings = PostgresSettings()
    es: ElasticsearchSettings = ElasticsearchSettings()
    cache: Cashe = Cashe()
    delay: int = 1
    page_size: int = 1000
    entities: Set[str] = ('film_work', 'person', 'genre')
    debug: str = Field('INFO', env='DEBUG')


settings = Settings()
