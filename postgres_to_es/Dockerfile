FROM python:3.10-buster

RUN mkdir /code \
    && groupadd -r web && useradd -d /code -r -g web web \
    && chown web:web -R /code 


WORKDIR /opt/app

COPY ./requirements.txt requirements.txt
RUN  pip3 install  --no-cache-dir -r requirements.txt

COPY . .

USER web

ENTRYPOINT ["python3", "etl/app.py"]
