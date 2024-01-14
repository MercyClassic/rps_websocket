FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTEDECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /game

COPY ./pyproject.toml /game/pyproject.toml

RUN apt update \
    && pip install poetry \
    && apt install -y vim \
    && apt install -y libmagic1 \
    && useradd -U app \
    && chown -R app:app /game \
    && chdir /game \
    && poetry config virtualenvs.create false \
    && poetry install --only main


COPY --chown=app:app . /game

WORKDIR /game/src

EXPOSE 8000

USER app

CMD ["sh", "/game/entrypoint.sh"]
