from abc import ABC, abstractmethod

import jwt

from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole


class BaseRBACManager(ABC):
    @abstractmethod
    async def authorize(self, token: str) -> str:
        """
        Decode authentication token and return user id
        :param token: Authentication token
        :return: User id
        """
        ...

    @abstractmethod
    async def filter_permissions(self, user_id: str = None, role_ids: list[str] = None) -> list[IRBACPermission]:
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
    async def get_user_roles(self, user_id: str) -> list[IRBACRole]:
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
    async def get_user_role_ids(self, user_id: str) -> list[int]:
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
