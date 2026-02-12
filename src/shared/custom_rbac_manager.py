from typing import Any, cast, Optional

import jwt
from starlette.requests import Request
from tortoise.expressions import Q

from entities.permissions import PermissionEntity, UserRoles, RoleEntity
from settings import get_now
from rbac.base_manager import BaseRBACManager, Access
from rbac.interfaces.permissions import IRBACPermission, IRBACRole


class CustomRBACManager(BaseRBACManager):
    async def fetch_user_access(self, user_id: Any = None, custom_meta: Optional[dict] = None) -> Access:
        user_roles = await self.get_user_roles(user_id)
        return {
            "permissions": await self.filter_permissions(user_id=user_id, role_ids=[i.id for i in user_roles]),
            "roles": user_roles,
            "user": None
        }

    async def authorize(self, token: str, request: Request | None = None, custom_meta: Optional[dict] = None) -> str:
        if request:
            try:
                request.state.token = token
            except AttributeError:
                pass
        decoded = jwt.decode(token.encode(), "KEY", algorithms=["HS256"])
        return decoded['subject_id']

    async def filter_permissions(self, user_id: Any | None = None, role_ids: list[Any] | None = None) -> list[IRBACPermission]:
        if isinstance(user_id, str):
            user_id = int(user_id)
        if role_ids is None:
            role_ids = []

        role_ids = [int(i) for i in cast(list[str], role_ids)]

        results = PermissionEntity.filter(Q(user_id=user_id) | Q(role_id__in=role_ids) & (Q(expires_at__isnull=True)) | Q(expires_at__gte=get_now()))

        results = await results.order_by('-created_at')

        return [i.to_interface() for i in results]


    async def get_user_roles(self, user_id: Any) -> list[IRBACRole]:
        if isinstance(user_id, str):
            user_id = int(user_id)

        user_role_ids: list[int] = [i.role_id for i in await UserRoles.filter(user_id=user_id)]

        user_roles: list[RoleEntity] = await RoleEntity.filter(Q(id__in=user_role_ids))
        return [i.to_interface() for i in user_roles]
