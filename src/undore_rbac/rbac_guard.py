from ascender.guards import Guard
from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing_extensions import deprecated

from undore_rbac.services.rbac_service import RbacService


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
        return await self.rbac.check_access(request.url.path, user_id, self.permissions, custom_meta={"org_id": 123})

@deprecated("Use RBACGuard Instead. Will soon be removed!")
class RbacGuard(RBACGuard):
    pass
