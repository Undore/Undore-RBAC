import jwt
from tortoise.expressions import Q

from entities.permissions import PermissionEntity, UserRoles, RoleEntity
from settings import get_now
from shared.rbac.base_manager import BaseRBACManager
from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole


class CustomRBACManager(BaseRBACManager):
    async def authorize(self, token) -> str:
        decoded = jwt.decode(token, "KEY", algorithms=["HS256"])
        return decoded['subject_id']

    async def filter_permissions(self, user_id: str = None, role_ids: list[str] = None) -> list[IRBACPermission]:
        user_id = int(user_id) if user_id else None
        if not role_ids:
            role_ids = []

        role_ids = [int(i) for i in role_ids]

        results = await PermissionEntity.filter(Q(user_id=user_id) | Q(role_id__in=role_ids),
                                                Q(expires_at__gte=get_now()))
        return [IRBACPermission.model_validate(i, from_attributes=True) for i in results]

    async def get_user_roles(self, user_id: str) -> list[IRBACRole]:
        user_id = int(user_id)

        user_role_ids: list[int] = [i.role_id for i in await UserRoles.filter(user_id=user_id)]

        user_roles: list[RoleEntity] = await RoleEntity.filter(Q(id__in=user_role_ids))
        return [IRBACRole.model_validate(i, from_attributes=True) for i in user_roles]
