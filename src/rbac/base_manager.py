from abc import ABC, abstractmethod
from typing import Any, TypedDict, Optional

from starlette.requests import Request

from rbac.interfaces.permissions import IRBACPermission, IRBACRole

class Access(TypedDict):
    permissions: list[IRBACPermission]
    roles: list[IRBACRole]
    user: Any | None  # Optional: not used within UndoreRBAC, but can be utilized to save requests

class BaseRBACManager(ABC):
    """
    Base class for RBAC custom manager.
    See /shared/custom_rbac_manager.py for example
    """

    @abstractmethod
    async def authorize(self, token: str, request: Optional[Request] = None) -> str:
        """
        Decode authentication token and return user id
        :param token: Authentication token
        :param request: Optional. Always provided from RBAC internally and can be used to avoid race conditions
        :return: User id
        """
        ...

    @abstractmethod
    async def fetch_user_access(self, user_id: Any) -> Access:
        """
        Fetch users' permissions, permissions of users' roles and users' roles in one request
        (Allowing for joined requests and optimization)

        WARNING: Make sure to also fetch permissions of users' roles, not only users' permissions

        See docs on self.filter_permissions and self.get_user_roles for
        proper permission filtering description

        :param user_id: User ID To fetch permissions and roles for
        :return:
        """
        ...

    @abstractmethod
    async def filter_permissions(self, user_id: Any = None, role_ids: list[Any] = None) -> list[IRBACPermission]:
        """
        Find permissions by matching user_id or some of role_ids
        Must search using OR filtering to gather all matching results

        Example for Tortoise, using Q

        async def filter_permissions(self, user_id: str = None, role_ids: list[str] = None) -> list[IRBACPermission]:
            if not role_ids:
                role_ids = []

            results = await PermissionEntity.filter(Q(user_id=user_id) | Q(role_id__in=role_ids))
            return [IRBACPermission.model_validate(i, from_attributes=True) for i in results]

        In this example, filtering all permissions matching user_id or  some of role_ids and validating response models

        :param user_id: User id to find
        :param role_ids: Role ids to find
        :return: List of permission names (e.g. ['moderation.ban', 'users.manage'])
        """
        ...

    @abstractmethod
    async def get_user_roles(self, user_id: Any) -> list[IRBACRole]:
        """
        Get roles for specific user id

        Example for Tortoise, using Q:

        async def get_user_roles(self, user_id: str) -> list[IRBACRole]:
            user_role_ids: list[int] = [i.role_id for i in await UserRoles.filter(user_id=user_id)]

            user_roles: list[RoleEntity] = await RoleEntity.filter(Q(id__in=user_role_ids))
            return [IRBACRole.model_validate(i, from_attributes=True) for i in user_roles]

        :param user_id: User id to search roles for
        :return: List of IRBACRole
        """
        ...

    @abstractmethod
    async def get_user_role_ids(self, user_id: Any) -> list[Any]:
        """
        Get role ids for specific user id
        Used by RBAC to save DB requests when full info is not needed

        Example for Tortoise:

        async def get_user_role_ids(self, user_id: str) -> list[int]:
            return [i.role_id for i in await UserRoles.filter(user_id=user_id)]

        :param user_id: User id to search roles for
        :return: List of role IDs
        """
        ...
