from tortoise import Model
from tortoise import fields


class PermissionEntity(Model):
    id: int = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("entities.UserEntity", related_name="permissions", null=True)
    role = fields.ForeignKeyField("entities.RoleEntity", related_name="permissions", null=True)
    permission = fields.TextField()
    value = fields.BooleanField(default=True)
    expires_at = fields.DatetimeField(null=True)


    class Meta:
        table = 'permissions'


class RoleEntity(Model):
    id: int = fields.BigIntField(pk=True)
    priority: int = fields.BigIntField()


    class Meta:
        table = 'roles'


class UserRoles(Model):
    role_id: int
    user_id: int

    id: int = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("entities.UserEntity", related_name="roles", null=True)
    role = fields.ForeignKeyField("entities.RoleEntity", related_name="roles", null=True)


    class Meta:
        table = 'users_roles'
