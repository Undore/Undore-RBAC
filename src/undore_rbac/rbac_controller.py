from ascender.core import Controller, Get

from undore_rbac.rbac_guard import RBACGuard
from undore_rbac.services.rbac_service import RbacService


@Controller(guards=[],
            imports=[],
            providers=[])
class RBACController:
    def __init__(self, rbac: RbacService):
        self.rbac = rbac

    @RBACGuard("undore_rbac.users.permissions.view")
    @Get('/users/{user_id}/permissions')
    async def main_endpoint(self, user_id: int):
        return {"success": True}
