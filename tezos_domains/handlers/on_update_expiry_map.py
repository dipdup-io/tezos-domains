from datetime import datetime

import strict_rfc3339  # type: ignore
from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff

import tezos_domains.models as models
from tezos_domains.types.name_registry.big_map.store_expiry_map_key import StoreExpiryMapKey
from tezos_domains.types.name_registry.big_map.store_expiry_map_value import StoreExpiryMapValue


async def on_update_expiry_map(
    ctx: HandlerContext,
    store_expiry_map: BigMapDiff[StoreExpiryMapKey, StoreExpiryMapValue],
) -> None:
    if not store_expiry_map.action.has_value:
        return
    assert store_expiry_map.key
    assert store_expiry_map.value

    expires_at = datetime.utcfromtimestamp(strict_rfc3339.rfc3339_to_timestamp(store_expiry_map.value.__root__))
    record_name = bytes.fromhex(store_expiry_map.key.__root__).decode()
    await models.Expiry.update_or_create(
        id=record_name,
        defaults={'expires_at': expires_at},
    )

    domain = await models.Domain.get_or_none(id=record_name).prefetch_related('records')
    if domain is not None:
        domain.expires_at = expires_at  # type: ignore
        await domain.save()
        if expires_at > datetime.utcnow():
            ctx.logger.debug('Updating expiration status for all records associated with domain %s (renewal)', domain.id)
            for record in domain.records:  # type: models.Record
                record.expired = False
                await record.save()
                if record.address is not None:
                    metadata = {} if record.metadata is None else record.metadata
                    metadata.update(name=record.id)
                    await ctx.update_contract_metadata(
                        network=ctx.datasource.network,
                        address=record.address,
                        metadata=metadata,
                    )
