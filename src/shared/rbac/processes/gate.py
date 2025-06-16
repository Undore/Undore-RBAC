from functools import cached_property

from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole, IRawRBACPermission
from shared.rbac.types.map import RBACMap


class RBACGate:
    def __init__(self, user_permissions: list[IRBACPermission], user_roles: list[IRBACRole], rbac_map: RBACMap):
        self.__user_permissions = user_permissions
        self.__user_roles = user_roles
        self.rbac_map = rbac_map

    @cached_property
    def roles(self) -> dict[int, IRBACRole]:
        """
        Get user roles in pairs of id and role

        :return: Dict of [roleId, IRBACRole]
        """
        return {i.id: i for i in self.__user_roles}

    @cached_property
    def permissions(self) -> dict[str, bool]:
        """
        Parses all user permissions with values, sorted by priority

        Calculated only once to save performance

        :return: Dict of [permission, value]
        """

        scoped_permissions = []
        shared_permissions = []

        for permission in self.__user_permissions:
            if permission.user_id:
                scoped_permissions.append(permission)
            if permission.role_id:
                shared_permissions.append(permission)
            else:
                raise ValueError(f"Invalid permission id={permission.id}. Permission must have either user_id or role_id")

        shared_permissions.sort(key=lambda permission: self.roles[permission.role_id].priority)
        # Make shared permissions arrange from lowest role priority to highest

        overrides: dict[str, bool] = {}

        for permission in shared_permissions + scoped_permissions:
            permission: IRBACPermission

            overrides[permission.permission] = permission.value

        return overrides

    def compare(self, permission: str):
        if not (permission := self.rbac_map.find(permission)):
            raise ValueError(f"Permission {permission} is not present in RBAC Map")

        permission: IRawRBACPermission

        return self.permissions.get(permission.permission, permission.config.default)
