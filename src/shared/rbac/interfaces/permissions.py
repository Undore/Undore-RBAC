from typing import Optional

from pydantic import BaseModel


class IRawRBACPermissionConfig(BaseModel):
    default: Optional[bool] = False


class IRawRBACPermission(BaseModel):
    permission: str
    config: IRawRBACPermissionConfig

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.permission}>"


class IRBACPermission(BaseModel):
    id: int
    permission: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    value: bool


class IRBACRole(BaseModel):
    id: str
    priority: int
