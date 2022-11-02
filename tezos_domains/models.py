from tortoise import fields
from dipdup.models import Model


class TLD(Model):
    id = fields.CharField(max_length=511, pk=True)
    owner = fields.CharField(max_length=36)

    # FIXME: Tortoise ORM uses "TLD" otherwise
    class Meta:
        table = 'tld'


class Expiry(Model):
    id = fields.CharField(max_length=512, pk=True)
    expires_at = fields.DatetimeField(null=True)


class Domain(Model):
    id = fields.CharField(max_length=511, pk=True)
    tld = fields.ForeignKeyField('models.TLD', 'domains')
    owner = fields.CharField(max_length=36)
    token_id = fields.BigIntField(null=True)
    expires_at = fields.DatetimeField(null=True)


class Record(Model):
    id = fields.CharField(max_length=511, pk=True)
    domain = fields.ForeignKeyField('models.Domain', 'records')
    address = fields.CharField(max_length=36, null=True, index=True)
    expired = fields.BooleanField(default=False)
    metadata = fields.JSONField(null=True)
