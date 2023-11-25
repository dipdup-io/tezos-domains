# FROM dipdup/dipdup:7
# FROM ghcr.io/dipdup-io/dipdup:7
FROM ghcr.io/dipdup-io/dipdup:aux-7.2.0

COPY --chown=dipdup pyproject.toml README.md .
RUN pip install .

COPY --chown=dipdup . tezos_domains
WORKDIR tezos_domains