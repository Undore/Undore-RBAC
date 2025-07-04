from tortoise import Model
from tortoise import fields

from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole


class PermissionEntity(Model):
    user_id: int
    role_id: int

    id: int = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("entities.UserEntity", related_name="permissions", null=True)
    role = fields.ForeignKeyField("entities.RoleEntity", related_name="permissions", null=True)
    permission = fields.TextField()
    value = fields.BooleanField(default=True)
    expires_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


    class Meta:
        table = 'permissions'

    def to_interface(self) -> IRBACPermission:
        return IRBACPermission(
            id=self.id,
            permission=self.permission,
            user_id=str(self.user_id) if self.user_id else None,
            role_id=str(self.role_id) if self.role else None,
            value=self.value,
            created_at=self.created_at
        )


class RoleEntity(Model):
    id: int = fields.BigIntField(pk=True)
    priority: int = fields.BigIntField()

    def to_interface(self) -> IRBACRole:
        return IRBACRole(
            id=str(self.id),
            priority=self.priority
        )

    class Meta:
        table = 'roles'


class UserRoles(Model):
    role_id: int
    user_id: int

    id: int = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("entities.UserEntity", related_name="roles", null=True)
    role = fields.ForeignKeyField("entities.RoleEntity", related_name="roles", null=True)


    class Meta:
        table = 'user_roles'
