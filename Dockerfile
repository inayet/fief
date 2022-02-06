FROM python:3.10-alpine

ARG FIEF_VERSION

WORKDIR /app

RUN apk update \
    && apk add --virtual build-deps build-base \
    && apk add --no-cache libffi-dev postgresql-dev mariadb-dev \
    && pip install --upgrade pip \
    && python --version \
    && pip install fief-server==${FIEF_VERSION} \
    && apk del build-deps

ENV PORT=80
EXPOSE ${PORT}

CMD [ "sh", "-c", "fief run-server --port $PORT" ]
