FROM dipdup/dipdup:7
# FROM ghcr.io/dipdup-io/dipdup:7
# FROM ghcr.io/dipdup-io/dipdup:next

RUN pip install strict_rfc3339

COPY --chown=dipdup . tezos_domains
WORKDIR tezos_domains