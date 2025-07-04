from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IRawRBACPermissionConfig(BaseModel):
    default: Optional[bool] = False
    explicit: Optional[bool] = False


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
    id: int
    permission: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    value: bool
    created_at: datetime


class IRBACRole(BaseModel):
    id: str
    priority: int
