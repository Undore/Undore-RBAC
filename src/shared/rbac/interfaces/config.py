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
    use_internal_exception_handler: If True, all RBACException exceptions will be handled in a specific format (See rbac_exception_handler_service for details)
    exception_handler_warning: Disaplay a warning, if the RBAC exception handler failed to start. Also affects exception handler debug message on start
    """
    rbac_map_path: str
    rbac_manager: Type[BaseRBACManager]
    log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = "DEBUG"
    use_internal_exception_handler: bool = True
    exception_handler_warning: bool = True

    @field_validator('rbac_manager')
    def validate_rbac_manager(cls, v):
        if not isinstance(v, type):
            raise TypeError("rbac_manager must be a class, not an instance.")
        if not issubclass(v, BaseRBACManager):
            raise TypeError("rbac_manager must be a subclass of BaseRBACManager")
        return v

    class Config:
        arbitrary_types_allowed = True
