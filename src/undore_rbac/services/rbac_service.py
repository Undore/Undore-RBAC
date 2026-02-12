from __future__ import annotations

from logging import Logger
from typing import Sequence, TYPE_CHECKING

from ascender.common import Injectable
from ascender.core import Service
from ascender.core.applications.application import Application
from ascender.core.di.injectfn import inject
from starlette.requests import Request

from undore_rbac.base_manager import BaseRBACManager
from undore_rbac.exceptions import InsufficientPermissions
from undore_rbac.interfaces.config import RBACConfig
from undore_rbac.logger import init_logger
from undore_rbac.types.rbac_map import RBACMap

if TYPE_CHECKING:
    from undore_rbac.rbac_exception_handler_service import RbacExceptionHandlerService
    from undore_rbac.processes.gate import RBACGate


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

        self.rbac_manager: BaseRBACManager = config.rbac_manager
        self.rbac_map = RBACMap(self.config.rbac_map_path)

        self.application.app.add_event_handler("startup", self.on_startup)

    def on_startup(self):
        self.logger = init_logger(self.config.log_level)

    async def check_access(self, request_url: str, user_id: str, permissions: Sequence[str], custom_meta: dict | None = None) -> RBACGate:
        """
        Check if user has specific permissions and raise an exception if not

        This method is used automatically by RBAC Guard.
        It is highly recommended to use RBACGate (can be initialized from user object) instead for permission checks in external ascender modules.

        RBACGate can contain a custom user object. See gate.user docs for info

        :param request_url: Request URL
        :param user_id: User ID to check
        :param permissions: Required permissions in RBACMap format (for example: test.modify)
        :param custom_meta: Custom metadata, which will be passed to the custom RBAC Manager. See BaseRBACManager docs for more info
        :return: Initialized User RBAC Gate if success.
        """
        from undore_rbac.processes.gate import RBACGate

        self.logger.debug(f"[bold cyan]Checking permissions for user id={user_id} on [bold magenta]{request_url}")

        gate = await RBACGate.from_user_id(user_id, custom_meta=custom_meta)

        for permission in permissions:
            if not gate.check_access(permission):
                raise InsufficientPermissions(request_url, (permission if self.config.expose_missing_permission else None))

        self.logger.info(f"[green]Access granted for user id={user_id}")

        return gate
