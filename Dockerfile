FROM python:3.6-alpine
MAINTAINER hrmthw <https://github.com/hrmthw>

RUN true \
  && mkdir -p /opt/leveldb_http \
  && chown 405 /opt/leveldb_http \
  && apk add --no-cache --virtual .build-deps gcc g++ musl-dev \
  && apk --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --update add leveldb leveldb leveldb-dev \
  && pip install pipenv

ADD . /opt/leveldb_http/
WORKDIR /opt/leveldb_http
RUN pipenv install --deploy --ignore-pipfile --python python3

EXPOSE 38081
CMD pipenv run python app.py

