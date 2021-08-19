from typing import Optional
from tortoise.functions import Max

import tezos_domains.models as models
from tezos_domains.types.name_registry.big_map.store_records_key import StoreRecordsKey
from tezos_domains.types.name_registry.big_map.store_records_value import StoreRecordsValue
from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff

record_counter: Optional[int] = None
token_counter: Optional[int] = None


async def next_record_update_id():
    global record_counter
    if record_counter is None:
        res = await models.Record.annotate(update_id=Max('update_id')).values('update_id')
        record_counter = int(res[0]['update_id']) if res else 0
    record_counter += 1
    return record_counter


async def next_token_update_id():
    global token_counter
    if token_counter is None:
        res = await models.TokenMetadata.annotate(update_id=Max('update_id')).values('update_id')
        token_counter = int(res[0]['update_id']) if res else 0
    token_counter += 1
    return token_counter


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
        ctx.logger.error('Invalid record `%s`: expected %s chunks, got %s', record_name, store_records.value.level, len(record_path))
        return

    if store_records.value.level == "1":
        await models.TLD.update_or_create(
            id=record_name,
            defaults=dict(owner=store_records.value.owner))
    else:
        if store_records.value.level == "2":
            token_id = int(store_records.value.tzip12_token_id) if store_records.value.tzip12_token_id else None
            if token_id is not None:
                update_id = await next_token_update_id()
                await models.TokenMetadata.update_or_create(
                    token_id=token_id,
                    defaults=dict(
                        contract=store_records.data.contract_address,
                        metadata={
                            "name": record_name,
                        },
                        update_id=update_id
                    ))

            expiry = await models.Expiry.get_or_none(id=record_name)
            expires_at = expiry.expires_at if expiry else None

            await models.Domain.update_or_create(
                id=record_name,
                defaults=dict(
                    tld_id=record_path[-1],
                    owner=store_records.value.owner,
                    token_id=token_id,
                    expires_at=expires_at
                )
            )

        update_id = await next_record_update_id()
        await models.Record.update_or_create(
            id=record_name,
            defaults=dict(
                domain_id='.'.join(record_path[-2:]),
                address=store_records.value.address,
                update_id=update_id
            )
        )
