from shared.rbac.interfaces.permissions import IRawRBACPermission


class RBACMap(list):
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
