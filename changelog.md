# Undore RBAC 1.2 Changelog
This is a major version, because a lot of architecture got changed

## RBACService deprecation
I considered it useless and improved `RBACGate` functionality instead:
- `RBACGate.check_access` now returns a `tuple` of `[Status, Reason]`, where `Status` is True or False, depending on if access was granted or not and `Reason` is the missing `IRawRBACPermission` (if access was denied, otherwise just None)
- `RBACGate.check_access` now has `auto_error`, which when True, will raise `InsufficientPermissions` if a permission is missing
- Added new docstrings and improved readability

## Minor changes
- `RbacGuard` (Not to be confused with `RBACGuard`) got **removed**
- `InsufficientPermissions` is now less dependent on FastAPI, not requiring request_url
- Applied all changes to docs and reworked example RBACGuard

### Thank you for your feedback. I'm looking forward to adding new features soon