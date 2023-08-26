from datetime import datetime
from typing import cast

from dipdup.context import HookContext
from dipdup.datasources.tezos_tzkt import TzktDatasource

from tezos_domains.models import Record


async def check_expiration(
    ctx: HookContext,
) -> None:
    ds = cast(TzktDatasource, next(iter(ctx.datasources.values())))
    expiring_records = (
        await Record.filter(expired=False, domain__expires_at__lt=datetime.utcnow()).all().prefetch_related('domain')
    )

    for record in expiring_records:
        ctx.logger.info('Record %s expired at %s', record.id, record.domain.expires_at)
        record.expired = True
        await record.save()
        if record.address:
            ctx.logger.debug('Invalidating contract metadata for %s @ %s', record.address, record.id)
            await ctx.update_contract_metadata(
                network=ds.network,
                address=record.address,
                metadata={},  # TODO: NULL
            )
