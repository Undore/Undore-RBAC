from typing import Type, Literal, Optional

from pydantic import BaseModel, field_validator

from shared.rbac.base_manager import BaseRBACManager


class RBACConfig(BaseModel):
    """
    Config for Undore RBAC
    Used in RbacModule.for_root

    rbac_map_path: Absolute path to rbac map YAML file
    rbac_manager: RBAC Manager class. Must be a subclass of BaseRBACManager
    log_level: RBAC Logging level
    """
    rbac_map_path: str
    rbac_manager: Type[BaseRBACManager]
    log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = "DEBUG"

    @field_validator('rbac_manager')
    def validate_rbac_manager(cls, v):
        if not isinstance(v, type):
            raise TypeError("rbac_manager must be a class, not an instance.")
        if not issubclass(v, BaseRBACManager):
            raise TypeError("rbac_manager must be a subclass of BaseRBACManager")
        return v

    class Config:
        arbitrary_types_allowed = True
