from ascender.core import Controller, Get

from shared.rbac.rbac_guard import RbacGuard
from shared.rbac.services.rbac_service import RbacService


@Controller(guards=[],
            imports=[],
            providers=[])
class RBACController:
    def __init__(self, rbac: RbacService):
        self.rbac = rbac

    @RbacGuard("undore_rbac.users.permissions.view")
    @Get('/users/{user_id}/permissions')
    async def main_endpoint(self, user_id: int):
        return {"success": True}
