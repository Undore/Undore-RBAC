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
from shared.rbac.types.rbac_map import RBACMap

#
#
#   ,999,         99  ,999, ,9999999,   ,999999999999,      _,999999,_      ,99999999999,      ,9999999,
#  dP''Y84        88 dP''Y8,8P'''''Y8b dP'''88''''''Y8b,  ,d8P''d8P'Y8b,   dP'''88''''''Y8,  ,dP''''''Y8b
#  Yb, '88        88 Yb, '8dP'     '88 Yb,  88       '8b,,d8'   Y8   '8b,dPYb,  88      '8b  d8'    4  Y8
#   ''  88        88  ''  88'       88  ''  88        '8bd8'    'Yb444d88P' ''  88      ,8P  88     'Y8P'
#       88        88      88        88      88         Y88P       '''''Y8       884444d8P'   '8b4444
#      88        88      88        88      88         d88b            d8       88''''Yb,   ,d8P''''
#       88        88      88        88      88        ,8PY8,          ,8P       88     '8b  d8'
#       88        88      88        88      88       ,8P''Y8,        ,8P'       88      '8i Y8,
#       Y8b,____,d88,     88        Y8,     88______,dP'  'Y8b,,__,,d8P'        88       Yb,'Yb4,,_____,
#        'Y888888P'Y8     88        'Y8    888888888P'      ''Y8888P''          88        Y8  ''Y8888888
#
#   ,99999999999,    ,99999999999,             ,999,       ,9999,
#  dP'''88''''''Y8, dP'''88''''''Y8,          dP''8I     ,88'''Y8b,
#  Yb,  88      '8b Yb,  88      '8b         dP   88    d8'     'Y8
#   ''  88      ,8P  ''  88      ,8P        dP    88   d8'   8b  d8
#       884444d8P'       884444d8P'        ,8'    88  ,8I    'Y88P'
#       88''''Yb,        88''''Y8b4        d88888888  I8'
#       88     '8b       88      '8b __   ,8'     88  d8
#       88      '8i      88      ,8PdP'  ,8P      Y8  Y8,
#       88       Yb,     88_____,d8'Yb,_,dP       '8b,'Yb4,,_____,
#       88        Y8    88888888P'   'Y8P'         'Y8  ''Y8888888


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
