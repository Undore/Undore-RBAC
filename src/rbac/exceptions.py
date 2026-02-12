from typing import Any

from fastapi import HTTPException
from starlette.requests import Request


class RBACHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, headers: dict[str, Any] = None, error_code: str | None = None, **kwargs):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        self.kwargs = kwargs
        self.error_code = error_code

    def __str__(self):
        return f"RBAC Exception {self.status_code}: {self.detail}"

    def __repr__(self):
        return f"<RBAC HTTP Exception {self.status_code}: {self.detail}>"

    def __dict__(self):
        details = {}
        if self.kwargs:
            details["details"] = self.kwargs

        return {
            "error": {
                "message": self.detail,
                "code": self.error_code or "RBAC",
                **details
            }
        }




class InsufficientPermissions(RBACHTTPException):
    def __init__(self, request_url: str, required_permission: str | None = None):
        self.missing_permission = required_permission
        self.request_url = request_url

        kw = {}
        if required_permission:
            kw['missing_permission'] = required_permission

        super().__init__(403, f"Insufficient permissions", **kw,
                         error_code="RBAC_ACCESS_DENIED")

    def __repr__(self):
        return f"403 <InsufficientPermissions route={self.request_url} missing={self.missing_permission}>"

    def __str__(self):
        return f"Missing permission: {self.missing_permission}"
