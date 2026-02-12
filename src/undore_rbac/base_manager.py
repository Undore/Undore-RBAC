from abc import ABC, abstractmethod
from typing import Any, TypedDict, Optional

from starlette.requests import Request

from undore_rbac.interfaces.permissions import IRBACPermission, IRBACRole

class Access(TypedDict):
    permissions: list[IRBACPermission]
    roles: list[IRBACRole]
    user: Any | None  # Optional: not used within UndoreRBAC, but can be utilized to save requests

class BaseRBACManager(ABC):
    """
    Base class for RBAC custom manager.
    See /shared/custom_rbac_manager.py for example
    """

    @abstractmethod
    async def authorize(self, token: str, request: Optional[Request] = None, custom_meta: Optional[dict] = None) -> Any:
        """
        Decode authentication token and return user id

        WARNING: Please take into account, that custom_meta can be None, because it is NOT passed when requesting authorization
        internally, like in the RBAC Exception Handler.

        If you REALLY need to carry the custom_meta in the exception authorization, you can use request.state

        :param token: Authentication token
        :param request: Optional. Always provided from RBAC internally and can be used to avoid race conditions
        :param custom_meta: Optional. Custom meta dict, can be passed when creating an RBACGate for flexibility
        :return: User id
        """
        ...

    @abstractmethod
    async def fetch_user_access(self, user_id: Any, custom_meta: Optional[dict] = None) -> Access:
        """
        Fetch users' permissions, permissions of users' roles and users' roles in one request
        (Allowing for joined requests and optimization)

        WARNING: Make sure to also fetch permissions, belonging to users' roles, not only users' permissions

        WARNING 2: Please take into account, that custom_meta can be None, because it is NOT passed when requesting access info internally

        :param user_id: User ID To fetch permissions and roles for
        :param custom_meta: Optional. Custom meta dict, can be passed when creating an RBACGate for flexibility
        :return: Access object
        """
        ...
