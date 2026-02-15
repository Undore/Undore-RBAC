# Undore RBAC

**RBAC made easy for Ascender Framework**

UndoreRBAC is a lightweight, configurable role-based access control (RBAC) system designed for seamless integration with the Ascender Framework.

Its goal is to **separate permission-evaluation logic and priority rules from data storage**, provide a flexible manager interface for fetching permissions/roles, and offer an easy-to-configure permission map.

---

## Core concepts

- **RBAC Map** - a YAML file that declares all available permissions and their configuration (`default`, `explicit`, `children`).
- **RBAC Manager** - the *user-implemented* bridge between your database and UndoreRBAC. You implement methods for authentication and for fetching roles/permissions.
- **RbacService** - the application-level service used by guards/middleware to perform access checks.
- **RBACGate** - an object that represents a single user’s access state; it performs comparison, inheritance, and override logic.
- **Permissions** carry a boolean `value` (True/False). This allows both granting and explicit denial of permissions.

---

## Basic behavior rules

1. **Priority** (from lower to higher; later items win in conflicts):
   - children permissions
   - roles (shared permissions) - roles with **higher** `priority` take precedence
   - scoped permissions (permissions assigned directly to the user)

2. **Wildcard** (`*`), e.g. `users.*`, means “everything under `users.`” - but a wildcard can be **overridden** by a permission marked `explicit` in the RBAC Map.

3. **`explicit: true`** - a permission marked explicit **ignores** wildcard/override propagation. Use with caution.

---

## Quick start

### 1) Implement `BaseRBACManager`

`BaseRBACManager` is an abstract class. You must implement:

- `authorize(token: str, request: Request | None = None, custom_meta: dict | None = None) -> user_id`
- `fetch_user_access(user_id: Any, custom_meta: dict | None = None) -> Access`

where `Access` contains:
```py
{
  "permissions": list[IRBACPermission],
  "roles": list[IRBACRole],
  "user": Any | None
}
```

**Note**
- Make sure `fetch_user_access` returns data in a predictable order if your logic depends on creation time or role priority. 
- The library can enforce `require_sorted_permissions` in RBACConfig by default, so it’s best if the manager returns sorted data.

---

## 2) Create `rbac_map.yml`

Permissions can be declared in two styles: nested YAML or dot-notation. Example:

```yaml
users:
  delete:
  view:
    other:

auth.login:

audit.export:
  _config:
    default: false
    explicit: true
    children:
      - users.view: true
      - users.delete: false
```

`_config` options:

- `default` - the default boolean value for this permission when the user has no record for it.
- `explicit` - if `true`, this permission **cannot** be obtained only via wildcard/children inheritance.
- `children` - a list of `permission:value` pairs that are applied automatically when this permission is present.

---

## 3) Initialization in Ascender Framework

In your `bootstrap.py`:

```python
from undore_rbac.interfaces.config import RBACConfig
from undore_rbac.rbac_module import RbacModule
from shared.custom_rbac_manager import CustomRBACManager
import os

appBootstrap: IBootstrap = {
    "providers": [
      RbacModule.for_root(
          RBACConfig(
              rbac_manager=CustomRBACManager(),
              rbac_map_path=os.path.join(BASE_PATH, "rbac_map.yml"),
              require_sorted_permissions=True
          )
      )
   ]
}
```

**Notes**
- `rbac_map_path` should point to the YAML file you prepared.
- `require_sorted_permissions=True` tells the library to expect manager-provided permission records in `created_at` order

---

## 4) Guard - usage examples

### Simple Guard

---

> **Note:** Refer official `Ascender Framework` docs for `Guard` and `ParamGuard` endpoint usage examples 

---
```py
class RBACGuard(Guard):
    def __init__(self, *permissions: str):
        self.permissions = permissions

    def __post_init__(self, rbac: RbacService):
        self.rbac = rbac

    async def can_activate(self, request: Request, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        user_id = await self.rbac.rbac_manager.authorize(token.credentials, request=request)
        await self.rbac.check_access(request.url.path, user_id, self.permissions)
        return True
```

### ParamGuard (recommended to avoid duplicated DB calls)

```py
class RBACParamGuard(ParamGuard):
    def __init__(self, *permissions: str):
        self.permissions = permissions

    def __post_init__(self, rbac: RbacService):
        self.rbac = rbac

    async def credentials_guard(self, request: Request, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        user_id = await self.rbac.rbac_manager.authorize(token.credentials, request=request)
        
        if self.permissions:
           gate = await self.rbac.check_access(request.url.path, user_id, self.permissions)
           user = gate.user
        else:  # Save performance if permission check is not needed
           user = ... # Your user GET logic
          
        # Your pydantic model for creds kwarg in endpoint
        return AuthCredentials(
            user=user
        )
```

> **Note:** `gate.user` is **not** populated automatically by the library. If you want `gate.user` available, your `fetch_user_access` implementation must return a `user` field inside the `Access` object.

---

## Detailed priority and override logic

1. Collect all permission records (scoped + shared) and roles for the user.
2. `RBACGate` calculates `children` (using the RBAC Map) for every permission.
3. Permissions are then applied in this order:
   - **Children** (applied first),
   - **Roles** (applied next - consider `role.priority` and assignment `created_at`),
   - **Scoped permissions** assigned directly to the user (applied last - strongest).
4. When conflicting permissions have the same effective priority, the most recent record (by `created_at`, or the order provided by the manager) wins.
   - If you rely on DB timestamps or insertion order, ensure `fetch_user_access` returns results in the expected order (Enabling `require_sorted_permissions` rises an exception if the sorting is wrong).

---

## Best practices & recommendations
- **Log** concise check summaries at debug level (do not log tokens or sensitive data).
- **Avoid overusing `explicit: true`** - it can silently block wildcard inheritance causing confusing denials.
- **Cache** `Access` per-request (e.g., in `request.state`) or use ParamGuard to prevent multiple DB hits in the same request.
---

---

## Common pitfalls and how to avoid them

1. **Wildcard permissions not taking effect** - check if the target permission has `_config.explicit: true` in the RBAC Map.
2. **`Permissions must be sorted by created_at` Exception** - ensure permissions are sorted as exception suggests or turn of this requirement in RBACConfig (not recommended)
3. **Heavy DB workload** - cache `Access` for the lifetime of the request or use ParamGuard to do a single fetch.

---

## Thank you for using UndoreRBAC.
Undore <github.com/Undore>
