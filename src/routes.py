from typing import Sequence
from ascender.core.router import RouterRoute
from controllers.main_controller import MainController
from rbac.rbac_controller import RBACController

routes: Sequence[RouterRoute | dict] = [
    {
        "path": "/",
        "controller": MainController,
        "tags": ["Main Controller"],
        "include_in_schema": True
    },
    {
        "path": "/RBAC",
        "controller": RBACController,
        "tags": ["UndoreRBAC Controller"],
        "include_in_schema": True
    },
]

__all__ = ["routes"]