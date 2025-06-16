from tortoise import Model
from tortoise import fields


class UserEntity(Model):
    id: int = fields.BigIntField(pk=True)
