from __future__ import annotations

import contextvars
from logging import Logger
from typing import Sequence, TYPE_CHECKING

from ascender.common import Injectable
from ascender.core import Service
from ascender.core.applications.application import Application
from ascender.core.di.injectfn import inject
from fastapi import HTTPException
from starlette.requests import Request

from shared.rbac.base_manager import BaseRBACManager
from shared.rbac.exceptions import InsufficientPermissions
from shared.rbac.interfaces.config import RBACConfig
from shared.rbac.logger import init_logger
from shared.rbac.types.rbac_map import RBACMap

if TYPE_CHECKING:
    from shared.rbac.rbac_exception_handler_service import RbacExceptionHandlerService
    from shared.rbac.processes.gate import RBACGate


@Injectable()
class RbacService(Service):
    """
    RBAC Service class is the main RBAC instance.
    This class is mostly used automatically by other RBAC services
    """
    logger: Logger
    handler: RbacExceptionHandlerService

    def __init__(self, application: Application, config: RBACConfig):
        self.config = config
        self.application = application

        self.handler: RbacExceptionHandlerService = inject("ExceptionHandler")

        self.request_scope = contextvars.ContextVar("request_token")

        self.rbac_manager: BaseRBACManager = config.rbac_manager()
        self.rbac_map = RBACMap(self.config.rbac_map_path)

        self.application.app.add_event_handler("startup", self.on_startup)

    def on_startup(self):
        self.logger = init_logger(self.config.log_level)

    async def check_access(self, request: Request, user_id: str, permissions: Sequence[str]) -> 'RBACGate':
        """
        Check if user has specific permissions and raise an exception if not

        This method is used automatically by RBAC Guard.
        It is highly recommended to use RBACGate (can be initialized from user object) instead for permission checks in external ascender modules.

        :param request: Starlette Request object
        :param user_id: User ID to check
        :param permissions: Required permissions in RBACMap format (for example: test.modify)
        :return: Initialized User RBAC Gate if success
        """
        from shared.rbac.processes.gate import RBACGate

        self.logger.debug(f"[bold cyan]Checking permissions for user id={user_id} on [bold magenta]{request.url.path}")

        gate = await RBACGate.from_user_id(user_id)

        for permission in permissions:
            if not gate.compare(permission):
                raise InsufficientPermissions(request, permission)

        self.logger.info(f"[green]Access granted for user id={user_id}")

        return gate
