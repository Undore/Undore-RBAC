from logging import Logger
from typing import Sequence

from ascender.common import Injectable
from ascender.core import Service
from ascender.core.applications.application import Application

from shared.rbac.interfaces.permissions import IRBACPermission, IRBACRole
from shared.rbac.utils._yaml import YAMLReader
from shared.rbac.base_manager import BaseRBACManager
from shared.rbac.interfaces.config import RBACConfig
from shared.rbac.logger import init_logger


@Injectable()
class RbacService(Service):
    logger: Logger

    def __init__(self, application: Application, config: RBACConfig):
        self.config = config
        self.application = application

        self.rbac_manager: BaseRBACManager = config.rbac_manager()
        self.yaml = YAMLReader(map_path=config.rbac_map_path)

        self.application.app.add_event_handler("startup", self.on_startup)

    def on_startup(self):
        self.logger = init_logger(self.config.log_level)

    async def check_access(self, user_id: str, permissions: Sequence[str]) -> bool:
        self.logger.info(f"[bold cyan]Checking permissions for user id={user_id}")

        user_roles: list[IRBACRole] = await self.rbac_manager.get_user_roles(user_id)
        user_role_ids: list[int] = [i.id for i in user_roles]
        user_permissions: list[IRBACPermission] = await self.rbac_manager.filter_permissions(user_id, user_role_ids)

        print(self.yaml.permission_map)


    async def edit_overrides(self, user_id: int, **overrides: dict):
        self.rbac_manager.add_permissions(user_id, permissions)
