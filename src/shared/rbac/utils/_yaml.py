from functools import cached_property

import yaml
from ascender.core.di.injectfn import inject

from shared.rbac.interfaces.permissions import IRawRBACPermission, IRawRBACPermissionConfig
from shared.rbac.types.map import RBACMap


class YAMLReader:
    def __init__(self, map_path: str):
        self.map_path = map_path

    def read_yaml(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)

    @cached_property
    def permission_map(self) -> RBACMap:
        """
        Read and flatten permission map
        :return: List of IRawRBACPermission
        """
        permission_map = self.read_yaml(self.map_path)

        def flatten_keys(d, parent_key="") -> list[IRawRBACPermission]:
            result = []

            for key, value in d.items():
                if key == "_config":
                    result.append(IRawRBACPermission(permission=parent_key, config=IRawRBACPermissionConfig(**value)))
                    continue

                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    result.extend(flatten_keys(value, full_key))
                else:
                    result.append(IRawRBACPermission(permission=full_key, config=IRawRBACPermissionConfig()))
            return result

        return RBACMap(flatten_keys(permission_map))
