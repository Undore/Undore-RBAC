from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

class IRBACChildPermission(BaseModel):
    permission: str
    value: bool

    @classmethod
    def from_rbac_map(cls, child: dict[str, bool] | str):
        if isinstance(child, str):
            return cls(permission=child, value=True)

        return cls(permission=list(child.keys())[0], value=list(child.values())[0])

class IRawRBACPermissionConfig(BaseModel):
    default: Optional[bool] = False
    explicit: Optional[bool] = False
    children: Optional[list[IRBACChildPermission]] = {}

    @classmethod
    def from_rbac_map(cls, **config):
        config.setdefault("children", [])

        config['children'] = [IRBACChildPermission.from_rbac_map(i) for i in config['children']]

        return cls(**config)

class IRawRBACPermission(BaseModel):
    permission: str
    config: IRawRBACPermissionConfig

    def __len__(self):
        return len(self.permission)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.permission == other
        return False

    def __repr__(self):
        return f"<RBACPermission {self.permission}>"

    def __str__(self):
        return self.permission


class IRBACPermission(BaseModel):
    id: Any
    permission: str
    user_id: Optional[Any] = None
    role_id: Optional[Any] = None
    value: bool
    created_at: datetime


class IRBACRole(BaseModel):
    id: Any
    priority: int
