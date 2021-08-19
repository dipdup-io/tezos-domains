from tortoise import Model, fields


class TLD(Model):
    id = fields.CharField(max_length=255, pk=True)
    owner = fields.CharField(max_length=36)


class Expiry(Model):
    id = fields.CharField(max_length=255, pk=True)
    expires_at = fields.DatetimeField(null=True)


class Domain(Model):
    id = fields.CharField(max_length=255, pk=True)
    tld = fields.ForeignKeyField('models.TLD', 'domains')
    owner = fields.CharField(max_length=36)
    token_id = fields.BigIntField(null=True)
    expires_at = fields.DatetimeField(null=True)


class Record(Model):
    id = fields.CharField(max_length=255, pk=True)
    domain = fields.ForeignKeyField('models.Domain', 'records')
    address = fields.CharField(max_length=36, null=True, index=True)
    update_id = fields.IntField(default=0)


class TokenMetadata(Model):
    token_id = fields.BigIntField(pk=True)
    contract = fields.CharField(max_length=36)
    update_id = fields.IntField(default=0)
    metadata = fields.JSONField()
