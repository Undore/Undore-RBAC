from undore_rbac.interfaces.permissions import IRawRBACPermission, IRawRBACPermissionConfig
from undore_rbac.rbac_default_map import DEFAULT_RBAC_MAP
from undore_rbac.utils.yaml_reader import YAMLReader

# TODO: ADD FOLDER MAPS SUPPORT


class RBACMap(list[IRawRBACPermission]):
    """
    RBAC map is a list of permissions, collected from YAML rbac_map file.
    It contains converted and parsed via YAMLReader values
    """
    def __init__(self, map_path: str):
        """
        Reads and flattens permission map
        :param map_path: Path to rbac_map.yml file
        """
        permission_map = DEFAULT_RBAC_MAP | (YAMLReader.read_yaml(map_path) or {})
        self.__validate_permissions(permission_map)

        permissions = self.__flatten_permissions(permission_map)

        super().__init__(permissions)

    def __validate_permissions(self, permissions: list[str]) -> bool:
        for permission in permissions:
            if "*" in permission:
                raise ValueError("Cannot have permission overrides in RBAC Map")

        return True

    def __flatten_permissions(self, d, prefix: str = "") -> list[IRawRBACPermission]:
        result = []

        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, bool) or value is None:
                result.append(
                    IRawRBACPermission(
                        permission=full_key,
                        config=IRawRBACPermissionConfig()
                    )
                )
                continue

            if not isinstance(value, dict):
                continue

            if "_config" in value:
                config_data = value["_config"]

                if config_data is not None and not isinstance(config_data, dict):
                    raise TypeError(f"{full_key}._config must be a mapping")

                config = IRawRBACPermissionConfig.from_rbac_map(**(config_data or {}))
            else:
                config = IRawRBACPermissionConfig()

            result.append(
                IRawRBACPermission(permission=full_key, config=config)
            )

            nested = {k: v for k, v in value.items() if k != "_config"}

            if nested:
                result.extend(self.__flatten_permissions(nested, full_key))

        return result

    def append(self, permission: str):
        raise ValueError("RBACMap is read-only")

    def pop(self, *args, **kwargs):
        raise ValueError("RBACMap is read-only")

    def insert(self, *args, **kwargs):
        raise ValueError("RBACMap is read-only")

    def extend(self, __object):
        raise ValueError("RBACMap is read-only")

    def find(self, permission: str) -> IRawRBACPermission | None:
        result = [i for i in self if i == permission]

        return result[0] if result else None

    def find_children_flattened(self, parent_permission: str) -> list[IRawRBACPermission]:
        parent_permission = parent_permission.removesuffix(".*")
        children = []

        for permission in self:
            if permission.config.explicit:
                continue

            if parent_permission == "*":
                children.append(permission)
                continue

            if permission.permission.startswith(parent_permission + "."):
                children.append(permission)

        return children
