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
        defaults=dict(expires_at=expires_at),
    )

    domain = await models.Domain.get_or_none(id=record_name)
    if domain is not None:
        domain.expires_at = expires_at  # type: ignore
        await domain.save()
