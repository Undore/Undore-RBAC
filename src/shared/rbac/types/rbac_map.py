from shared.rbac.interfaces.permissions import IRawRBACPermission, IRawRBACPermissionConfig
from shared.rbac.rbac_default_map import DEFAULT_RBAC_MAP
from shared.rbac.utils.yaml_reader import YAMLReader

# TODO: ADD FOLDER MAPS SUPPORT


class RBACMap(list):
    """
    RBAC map is a list of permissions, collected from YAML rbac_map file.
    It contains converted and parsed via YAMLReader values
    """
    def __init__(self, map_path: str):
        """
        Reads and flattens permission map
        :param map_path: Path to rbac_map.yml file
        """
        permission_map = DEFAULT_RBAC_MAP | YAMLReader.read_yaml(map_path)
        self.__validate_permissions(permission_map)

        permissions = self.__flatten_permissions(permission_map)

        super().__init__(permissions)

    def __validate_permissions(self, permissions: list[str]) -> bool:
        for permission in permissions:
            if "*" in permission:
                raise ValueError("Cannot have permission overrides in RBAC Map")

        return True

    def __flatten_permissions(self, d) -> list[IRawRBACPermission]:
        result = []

        for full_key, value in d.items():
            if value is None:
                config = IRawRBACPermissionConfig()
            else:
                config = IRawRBACPermissionConfig(**value)

            result.append(IRawRBACPermission(permission=full_key, config=config))

        return result

    def append(self, permission: str):
        raise ValueError("RBACMap is read-only")

    def pop(self, __index: int = -1):
        raise ValueError("RBACMap is read-only")

    def insert(self, __index: int, __object):
        raise ValueError("RBACMap is read-only")

    def extend(self, __object):
        raise ValueError("RBACMap is read-only")

    def find(self, permission: str) -> IRawRBACPermission | None:
        result = [i for i in self if i == permission]

        return result[0] if result else None
