from typing import Optional

from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff
from tortoise.functions import Max

import tezos_domains.models as models
from tezos_domains.types.name_registry.big_map.store_records_key import StoreRecordsKey
from tezos_domains.types.name_registry.big_map.store_records_value import StoreRecordsValue


async def on_update_records(
    ctx: HandlerContext,
    store_records: BigMapDiff[StoreRecordsKey, StoreRecordsValue],
) -> None:
    if not store_records.action.has_value:
        return
    assert store_records.key
    assert store_records.value

    record_name = bytes.fromhex(store_records.key.__root__).decode()
    record_path = record_name.split('.')
    ctx.logger.info('Processing `%s`', record_name)

    if len(record_path) != int(store_records.value.level):
        ctx.logger.error(
            'Invalid record `%s`: expected %s chunks, got %s',
            record_name,
            store_records.value.level,
            len(record_path),
        )
        return

    if store_records.value.level == "1":
        await models.TLD.update_or_create(
            id=record_name,
            defaults=dict(
                owner=store_records.value.owner,
            ),
        )
    else:
        if store_records.value.level == "2":
            token_id = int(store_records.value.tzip12_token_id) if store_records.value.tzip12_token_id else None
            if token_id is not None:
                await ctx.update_token_metadata(
                    address=store_records.data.contract_address,
                    token_id=token_id,
                    metadata={'name': record_name},
                )

            expiry = await models.Expiry.get_or_none(id=record_name)
            expires_at = expiry.expires_at if expiry else None

            await models.Domain.update_or_create(
                id=record_name,
                defaults=dict(
                    tld_id=record_path[-1],
                    owner=store_records.value.owner,
                    token_id=token_id,
                    expires_at=expires_at,
                ),
            )

        await models.Record.update_or_create(
            id=record_name,
            defaults=dict(
                domain_id='.'.join(record_path[-2:]),
                address=store_records.value.address,
            ),
        )
