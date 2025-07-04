from tortoise import Model
from tortoise import fields


class UserEntity(Model):
    id: int = fields.BigIntField(pk=True)
    name: str = fields.TextField()


    class Meta:
        table = 'users'
