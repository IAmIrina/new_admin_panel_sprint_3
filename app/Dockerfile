FROM python:3.10-buster

RUN mkdir /code \
    && groupadd -r web && useradd -d /code -r -g web web \
    && chown web:web -R /code 


WORKDIR /opt/app

COPY ./requirements.txt requirements.txt
RUN  pip3 install  --no-cache-dir -r requirements.txt

RUN mkdir static \
    && chown web:web -R static

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

COPY . .

EXPOSE 8000

USER web

ENTRYPOINT ["uwsgi"]
CMD ["--strict", "--ini", "uwsgi.ini"]
