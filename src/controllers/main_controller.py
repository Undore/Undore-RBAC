import jwt
from ascender.core import Controller, Get

from entities.users import UserEntity
from undore_rbac.rbac_guard import RBACGuard
from undore_rbac.services.rbac_service import RbacService


@Controller(guards=[],
            imports=[],
            providers=[])
class MainController:
    def __init__(self, rbac: RbacService):
        self.rbac = rbac

    @Get("/login")
    async def login(self):
        new_user = await UserEntity.create(name="User")

        payload = {"subject_id": new_user.id}
        secret_key = "KEY"
        algorythm = "HS256"
        return jwt.encode(payload, secret_key, algorithm=algorythm)

    @RBACGuard("users.view", "users.manage")
    @Get()
    async def main_endpoint(self):
        return {"success": True}
