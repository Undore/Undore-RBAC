from ascender.core import Controller, Get

from entities.users import UserEntity
from rbac.rbac_guard import RbacGuard
from rbac.services.rbac_service import RbacService

import jwt


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

    @RbacGuard("users.view")
    @Get()
    async def main_endpoint(self):


        return {"success": True}
