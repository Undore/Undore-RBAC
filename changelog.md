# Undore RBAC 1.2.7 Changelog
This is a patch, covering some security-related fixes and permission check expansions

## RBACGate.check_access now allows checking wildcard access
You can now check if the user has access to all children permissions of some permission via RBACGate.check_access

```python
# Example

    gate = await RBACGate.from_user_id(...)

    gate.check_access("users.*")
    gate.check_access("*")
    gate.check_access("users")
```
In this example, first call will only return True (not raise an exception) if the user has all children permissions of permission `user`,
for example, `user.read, user.delete etc.` (Depends on your rbac map)

`*` permission will require a user to have ALL permissions present in rba map

> **Note:** take into account the next change when using this feature

## Wildcards now also grant access to same-level permissions 
If you have an RBACMap like this:
```yaml
users:
  edit:
  view:
    others:
```
And you request a permission check for permission `users.view`, when the user has a wildcard for `users.view.*`,
result will be True, because `users.view.*` granted access to `users.view`, which is on the same level as `users.view.*`

This change was made to make the above feature work properly

## Security fix: Priority is now properly handled as described in README

## Small optimization changes, removal of default RBAC Map

> **End of 1.2.7 changelog**

# Undore RBAC 1.2 Changelog
This is a major version. Architecture got changed quite a bit

## RBACService deprecation
I considered it useless and improved `RBACGate` functionality instead:
- `RBACGate.check_access` now returns a `tuple` of `[Status, Reason]`, where `Status` is True or False, depending on if access was granted or not and `Reason` is the missing `IRawRBACPermission` (if access was denied, otherwise just None)
- `RBACGate.check_access` now has `auto_error`, which when True, will raise `InsufficientPermissions` if a permission is missing
- Added new docstrings and improved readability

## Minor changes
- `RbacGuard` (Not to be confused with `RBACGuard`) got **removed**
- `InsufficientPermissions` is now less dependent on FastAPI, not requiring request_url
- Applied all changes to docs and reworked example RBACGuard
- Updated to ascender 1.2.1b1 (in v1.2.5)

### Thank you for your feedback. I'm looking forward to adding new features soon