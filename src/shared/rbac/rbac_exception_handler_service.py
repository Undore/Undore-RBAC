from logging import Logger

from ascender.common import Injectable
from ascender.core import Service
from ascender.core.applications.application import Application
from ascender.core.di.injectfn import inject
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse

from shared.rbac.logger import init_logger
from shared.rbac.exceptions import RBACHTTPException
from shared.rbac.services.rbac_service import RbacService


@Injectable()
class RbacExceptionHandlerService(Service):
    logger: Logger = init_logger("DEBUG")

    def __init__(self, application: Application):
        self.app = application


        self.app.app.add_exception_handler(RBACHTTPException, self.handle)

    async def handle(self, request: Request, exc: Exception):
        if not isinstance(exc, RBACHTTPException):
            return None

        user_id = None

        rbac = inject(RbacService)
        token = rbac.request_scope.get()

        if token:
            user_id = await rbac.rbac_manager.authorize(token)

        self.logger.info(f"[bold red]RBAC Exception{' for user id={}'.format(user_id) if user_id else ''}[/bold red]: {exc}")  # War crime

        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.__dict__()),
            headers=exc.headers
        )
