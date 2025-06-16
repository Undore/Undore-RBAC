from ascender.guards import Guard
from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.rbac.rbac_service import RbacService


# noinspection PyMethodOverriding
class RbacGuard(Guard):
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

    async def can_activate(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """
        Works same as FastAPI's Dependency Injection
        """
        user_id = await self.rbac.rbac_manager.authorize(token.credentials)
        return await self.rbac.check_access(user_id, self.permissions)
