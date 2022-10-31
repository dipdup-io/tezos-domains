from dipdup.context import HookContext
from dipdup.datasources.tzkt.datasource import TzktDatasource

from typing import cast
from tezos_domains.models import Domain
from datetime import datetime


async def check_expiration(
    ctx: HookContext,
) -> None:
    ds = cast(TzktDatasource, next(iter(ctx.datasources.values())))
    expired_domains = await Domain.filter(expires_at__lt=datetime.utcnow()).all().prefetch_related('records')
    for domain in expired_domains:
        ctx.logger.info('Domain %s expired %s', domain.id, domain.expires_at)
        for record in domain.records:
            if record.address:
                ctx.logger.info('Invalidating contract metadata for %s @ %s', record.address, record.id)
                await ctx.update_contract_metadata(
                    network=ds.network,
                    address=record.address,
                    metadata={},  # TODO: NULL
                )
