from ascender.core import AscModule
from ascender.core.applications.application import Application
from ascender.core.di.interface.provider import Provider

from shared.rbac.interfaces.config import RBACConfig
from shared.rbac.rbac_service import RbacService

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


@AscModule(
    imports=[],
    declarations=[],
    providers=[],
    exports=[]
)
class RbacModule:
    @staticmethod
    def for_root(config: RBACConfig) -> Provider:
        return [
            {
                "provide": RbacService,
                "use_factory": lambda application: RbacService(application, config),
                "deps": [Application]}
        ]
