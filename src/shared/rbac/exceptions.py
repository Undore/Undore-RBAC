from typing import Any

from fastapi import HTTPException
from starlette.requests import Request


class RBACHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: dict[str, Any] = None, **kwargs):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        self.kwargs = kwargs

    def __str__(self):
        return f"RBAC Exception {self.status_code}: {self.detail}"

    def __repr__(self):
        return f"<RBACHTTPException {self.status_code}: {self.detail}>"

    def __dict__(self):
        return {
            "status_code": self.status_code,
            "detail": self.detail,
            **self.kwargs
        }




class InsufficientPermissions(RBACHTTPException):
    def __init__(self, request: Request, required_permission: str):
        self.missing_permission = required_permission
        self.request = request

        super().__init__(403, f"Insufficient permissions", missing_permission=required_permission)

    def __repr__(self):
        return f"403 <InsufficientPermissions route={self.request.url.path} missing={self.missing_permission}>"


    def __str__(self):
        return f"Missing permission: {self.missing_permission}"
