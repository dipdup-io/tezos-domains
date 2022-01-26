FROM ghcr.io/dipdup-net/dipdup-py:pr-219

COPY pyproject.toml poetry.lock ./
RUN inject_pyproject

COPY tzprofiles_indexer tzprofiles_indexer
COPY dipdup.yml dipdup.prod.yml ./
