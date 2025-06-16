from ascender.core import AscModule
from ascender.core.applications.application import Application
from ascender.core.di.interface.provider import Provider

from shared.rbac.interfaces.config import RBACConfig
from shared.rbac.rbac_service import RbacService


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
