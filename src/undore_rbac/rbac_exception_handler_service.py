from logging import Logger

from ascender.common import Injectable
from ascender.core import Service
from ascender.core.applications.application import Application
from ascender.core.di.injectfn import inject
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse

from undore_rbac.interfaces.config import RBACConfig
from undore_rbac.logger import init_logger
from undore_rbac.exceptions import RBACHTTPException
from undore_rbac.services.rbac_service import RbacService


@Injectable()
class RbacExceptionHandlerService(Service):
    logger: Logger = init_logger("DEBUG")

    def __init__(self, application: Application):
        self.app = application
        config = inject(RBACConfig)

        if config.exception_handler_config.use:
            if config.exception_handler_config.enable_usage_warning:
                self.logger.debug("Using Internal Exception Handler. For more info, see RBACConfig")
            self.app.app.add_exception_handler(RBACHTTPException, self.handle)
        elif config.exception_handler_config.enable_usage_warning:
            self.logger.warning("[bold yellow]RBAC Exception handler is not being used. RBACExceptions may have unexpected behaviour, like not displaying the missing permission."
                                "\nFor info or to disable this warning, see RBACConfig in RBACModule.for_root()")

    async def handle(self, request: Request, exc: Exception):
        if not isinstance(exc, RBACHTTPException):
            return None

        user_id = None

        rbac = inject(RbacService)

        token = None
        try:
            token = request.state.token
        except AttributeError:
            pass

        if token:
            user_id = await rbac.rbac_manager.authorize(token, request=request)

        self.logger.info(f"[bold red]RBAC Exception handled{' for user id={}'.format(user_id) if user_id else ''}[/bold red]: [yellow]{exc}")  # War crime

        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.__dict__()),
            headers=exc.headers
        )
