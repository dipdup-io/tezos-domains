# generated by datamodel-codegen:
#   filename:  store_records_value.json

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Extra


class StoreRecordsValue(BaseModel):
    class Config:
        extra = Extra.forbid

    address: str | None
    data: dict[str, str]
    expiry_key: str | None
    internal_data: dict[str, str]
    level: str
    owner: str
    tzip12_token_id: str | None
