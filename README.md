# Project work: "Admin Panel and ETL for Online Cinema".

app folder contents Admin panel source code for the online cinema content. The admin panel implements an admin web interface and CRUD operations. 
postgres_to_es contains an ETL source code service that extracts changed data from the Postgres database and puts it into the Elastic Search index.

## Stack

- Django
- Postgres
- Elastic Search
- NGINX
- Docker

## Elastic Search index schema

[index schema](https://code.s3.yandex.net/middle-python/learning-materials/es_schema.txt)💾

## Сrash recovery
ETL implements backoff decorator which used to wrap database or ElasticSearch connections. ETL emplements save state so after restart ETL starts from the stop point.

## Tests
[ES Postman-tests](https://code.s3.yandex.net/middle-python/learning-materials/ETLTests-2.json)💾.