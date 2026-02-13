from typing import Literal, Optional, TypedDict

from pydantic import BaseModel, field_validator

from undore_rbac.base_manager import BaseRBACManager

class RBACExceptionHandlerConfig(BaseModel):
    """
    Part of RBACConfig

    use: If True, all RBACException exceptions will be handled in a specific format (See rbac_exception_handler_service for details)
    enable_usage_warning: Log a warning, if the RBAC exception handler failed to start. Also affects exception handler debug message on start
    expose_missing_permission: When raising an RBAC Access Denied exception, whether to show which permission is missing
    """
    use: bool = True
    enable_usage_warning: bool = True
    expose_missing_permission: bool = True

class RBACConfig(BaseModel):
    """
    Config for Undore RBAC
    Used in RbacModule.for_root

    rbac_map_path: Absolute path to rbac map YAML file
    rbac_manager: RBAC Manager INSTANCE. Must be a subclass of BaseRBACManager
    log_level: RBAC Logging level
    log_level: See RBACExceptionHandlerConfig for details
    """
    rbac_map_path: str
    rbac_manager: BaseRBACManager
    log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = "DEBUG"
    exception_handler_config: RBACExceptionHandlerConfig = RBACExceptionHandlerConfig()

    @field_validator('rbac_manager')
    def validate_rbac_manager(cls, v):
        if not isinstance(v, BaseRBACManager):
            raise TypeError("rbac_manager must be a subclass of BaseRBACManager")
        return v

    class Config:
        arbitrary_types_allowed = True
