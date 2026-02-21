from ascender.guards import Guard
from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from undore_rbac.exceptions import InsufficientPermissions
from undore_rbac.services.rbac_service import RbacService
from undore_rbac.processes.gate import RBACGate

# noinspection PyMethodOverriding
class RBACGuard(Guard):
    rbac: RbacService

    def __init__(self, *permissions: str):
        """
        Use __init__ for accepting parameters of guard decorator
        """
        self.permissions = permissions

    def __post_init__(self, rbac: RbacService):
        """
        Handle dependency injections, use for injecting DIs
        """
        self.rbac = rbac
        self.logger = self.rbac.logger

    async def can_activate(self, request: Request, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """
        Works same as FastAPI's Dependency Injection
        """
        user_id = await self.rbac.rbac_manager.authorize(token.credentials, request=request, custom_meta={"org_id": 123})

        self.logger.debug(f"[bold cyan]Checking permissions for user id={user_id} on [bold magenta]{request.url.path}")

        gate = await RBACGate.from_user_id(user_id, custom_meta={"org_id": 123})
        status, reason = gate.check_access(self.permissions)
        if status is False:
            raise InsufficientPermissions(request_url=request.url.path, required_permission=reason)
