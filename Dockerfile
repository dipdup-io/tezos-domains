FROM ghcr.io/dipdup-net/dipdup-py:pr-219

COPY pyproject.toml poetry.lock ./
RUN inject_pyproject

COPY tezos_domains tezos_domains
COPY dipdup.yml dipdup.prod.yml ./
