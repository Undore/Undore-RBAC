import os

from ascender.common.api_docs import DefineAPIDocs
from ascender.core.database import provideDatabase, ORMEnum
from ascender.core.router import provideRouter
from ascender.core.types import IBootstrap

from routes import routes
from settings import DATABASE_CONNECTION, BASE_PATH
from shared.custom_rbac_manager import CustomRBACManager
from undore_rbac.interfaces.config import RBACConfig
from undore_rbac.rbac_module import RbacModule


appBootstrap: IBootstrap = {
    "providers": [
        {
            "provide": DefineAPIDocs,
            "value": DefineAPIDocs(),
        },
        RbacModule.for_root(
            RBACConfig(
                rbac_manager=CustomRBACManager(),
                rbac_map_path=os.path.join(BASE_PATH, "rbac_map.yml")
            )),
        provideRouter(routes),
        provideDatabase(ORMEnum.TORTOISE, DATABASE_CONNECTION)
    ]
}