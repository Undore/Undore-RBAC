from functools import cached_property
from typing import Union, Any

from ascender.core.di.injectfn import inject

from shared.rbac.base_manager import Access
from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole, IRawRBACPermission, IRBACChildPermission
from shared.rbac.services.rbac_service import RbacService
from shared.rbac.types.rbac_map import RBACMap


class RBACGate:
    """
    RBACGate Class can be used to check permissions for a specific user outside endpoints.
    For example, to check additional access conditions.
    Initialized once with certain permissions.

    Keep in mind that if permissions changed, you need to update overrides using the method update_overrides
    for changes to take effect. Roles and permissions properties are strictly read-only.
    """
    rbac_service: RbacService = inject(RbacService)

    def __init__(self, *, user_permissions: list[IRBACPermission], user_roles: list[IRBACRole], rbac_map: RBACMap, custom_user: Any | None = None):
        self.__user_permissions = user_permissions
        self.__user_roles = user_roles
        self.__custom_user: Any | None = custom_user
        self.rbac_map = rbac_map

    @property
    def user(self) -> Any | None:
        """
        Returns a custom User Object, if invoked in Access TypedDict within rbac_manager.fetch_user_access
        For this to work, make sure to provide user in Access TypedDict, when fetching user access in a custom RBAC Manager
        :return: Custom User Object (any) or None, if not provided in RBAC Custom Manager
        """
        return self.__custom_user

    @classmethod
    async def from_user_id(cls, user_id: Any) -> "RBACGate":
        rbac_manager = cls.rbac_service.rbac_manager

        user_access = await rbac_manager.fetch_user_access(user_id)
        user_roles: list[IRBACRole] = user_access['roles']
        user_permissions: list[IRBACPermission] = user_access['permissions']
        user: Any | None = user_access['user']

        return cls(user_permissions=user_permissions, user_roles=user_roles, rbac_map=cls.rbac_service.rbac_map, custom_user=user)

    @classmethod
    async def from_access(cls, access: Access) -> "RBACGate":
        user_roles: list[IRBACRole] = access['roles']
        user_permissions: list[IRBACPermission] = access['permissions']
        user: Any | None = access['user']

        return cls(user_permissions=user_permissions, user_roles=user_roles, rbac_map=cls.rbac_service.rbac_map, custom_user=user)

    @cached_property
    def user_roles(self) -> dict[str, IRBACRole]:
        """
        Get user roles in pairs of id and role

        Calculated only once to save performance. Use update_overrides to update this.

        :return: Dict of [roleId, IRBACRole]
        """
        return {i.id: i for i in self.__user_roles}


    def update_overrides(self, *, user_permissions: Union[list[IRBACPermission], False], user_roles: Union[list[IRBACRole], False]) -> None:
        """
        Update permissions and roles read-only attributes

        This method can be used if permissions or roles changed and
        you need changes to take effect in current gate instance
        without making excessive database requests.

        :param user_roles: New user roles. If False, keep current
        :param user_permissions: New user permissions (including user roles permissions). If False, keep current
        :return: None
        """
        self.__user_roles = user_roles
        self.__user_permissions = user_permissions
        del self.user_roles
        del self.user_permissions

        # TODO: TEST THIS

    @cached_property
    def user_permissions_dict(self) -> dict[str, bool]:
        """
        self.user_permissions, but not sorted by priority and as a dict
        :return: Dict of [rawPermission, Value]
        """
        return {k: v for k, v in self.user_permissions}

    @cached_property
    def user_permissions(self) -> list[tuple[str, bool]]:
        """
        Parses all user permissions with values, sorted by priority

        Takes in account permission values and role priority overrides
        This means, that permission values will be sorted in this order:
        1. Child permissions: Permissions, defined as child permissions in RBAC Map for parent permission, which user has
        2. Role (shared) permissions: Ones with the highest role priority are the last, if same - last one is the newest
        3. User permissions
        Last permissions override previous, so user permissions are the highest priority and child permissions are the lowest (priority)
        The higher is group priority, the more important it is (in sense of overrides)

        Calculated only once to save performance. Use update_overrides to update this.

        :raises ValueError: If permission is invalid
        :return: Dict of [permission, value]
        """

        scoped_permissions: list[IRBACPermission] = []
        shared_permissions: list[IRBACPermission] = []
        child_permissions: list[IRBACChildPermission] = []

        for permission in self.__user_permissions:
            permission: IRBACPermission

            map_permission = self.rbac_map.find(permission.permission)
            if not map_permission and not permission.permission.endswith("*"):
                raise ValueError(f"Permission {permission.permission} not found in RBAC Map")
            elif map_permission:
                if map_permission.config.children is not None and permission.value is True:
                    child_permissions.extend(map_permission.config.children)

            if permission.user_id:
                scoped_permissions.append(permission)
            elif permission.role_id:
                shared_permissions.append(permission)
            else:
                raise ValueError(
                    f"Invalid permission id={permission.id}. Permission must have either user_id or role_id")

        shared_permissions.sort(key=lambda permission: self.user_roles[permission.role_id].priority)
        # Make shared permissions arrange from the lowest role priority to highest

        scoped_permissions_copy = scoped_permissions.copy()
        scoped_permissions.sort(key=lambda permission: permission.created_at, reverse=True)

        if scoped_permissions_copy != scoped_permissions:
            raise RuntimeError("IRBACPermissions must be sorted by created_at (Newer ones first). Please, implement this in your manager")

        permissions_sorted: list[tuple[str, bool]] = []

        # Combine and override all permissions with the highest priority values
        for permission in child_permissions + shared_permissions + scoped_permissions:
            permission: IRBACPermission

            raw_permissions = [i[0] for i in permissions_sorted]
            if permission.permission in raw_permissions:
                continue

            permissions_sorted.append((permission.permission, permission.value))

        return permissions_sorted

    def compare(self, required_permission: str) -> bool:
        """
        Checks if user has specific permission.
        Takes overrides, values, roles, permission configs and priorities into account

        :raises ValueError: If permission is not present in RBAC Map
        :param required_permission: RBAC Permission to check
        :return: True if access granted, otherwise False
        """

        # noinspection PyTypeChecker
        if not (_permission := self.rbac_map.find(required_permission)):
            raise ValueError(f"Permission {required_permission} is not present in RBAC Map")

        _permission: IRawRBACPermission

        if not _permission.config.explicit:
            # Do not check overrides, if explicit permission

            override_permissions = [i for i in self.user_permissions if i[0].endswith("*")]

            override = self.__check_permission_overriding(required_permission, override_permissions)
            if override is not None:
                return override


        if self.user_permissions_dict.get(_permission.permission, _permission.config.default):
            return True

        return False


    def __check_permission_overriding(self, required_permission: str, overrides: list[tuple[str, bool]]) -> bool | None:
        """
        Applies overrides (permissions ending with *, overriding children permissions as True)
        to certain permission to check if any of the overrides cover this permission

        WARNING: Takes Values into account, so override with False value will false-override all children permissions
        This method will not be automatically called if permission is Explicit
        WARNING 2: All overrides must be sorted in order of priority (most important are first)

        For example:

        permission = users.view
        overrides = ["users.*", "moderation.*"]
        Result: True (Because users.* covers users.view)

        :param required_permission: Original permission
        :param overrides: Permission overrides (permissions ending with *). List of tuples of [RawPermission, Value]
        :raises ValueError: If an override does not end with *
        :return: True if permission is overridden as True, False if overridden as False, None if not overridden
        """
        permission_parts = required_permission.split(".")
        total_permission_parts = len(permission_parts)

        for override, value in overrides:
            if not override.endswith("*"):
                raise ValueError("Override must end with *")

            for p_index, part in enumerate(override.split(".")):
                if total_permission_parts - 1 < p_index:
                    # No point in checking further, because override part index is out of range
                    break

                if part == "*" and p_index <= total_permission_parts:
                    # p_index here is the index of current part, which is *
                    # To compare previous override level (index) to required_permission parts,
                    # subtract 1 from p_index, but total_permission_parts also requires subtracting 1
                    # to account for length being +1 of index length, so there is two -1 on both sides and they just equalize

                    # Basically, the ride side of this comparison could look like this:
                    # (p_index - 1) <= (total_permission_parts - 1)

                    return value

                if part != permission_parts[p_index]:
                    break

        return None
