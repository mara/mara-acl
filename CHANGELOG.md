# Changelog

## 2.1.1 (2022-06-17)

- fix add missing folders in setuptools build
- fix PyPI readme images (requires a new version)

## 2.1.0 (2022-03-16)

- fix issue with untracked folder `.eggs/` since version 2.0.1
- make the login process patchable. With his it is possible to implement a custom authentication handling

## 2.0.1 (2020-01-24)

- Include all versioned package files in wheel (not only python files)


## 2.0.0 (2019-04-12)

- Change MARA_XXX variables to functions to delay importing of imports

**required changes** 

- Update `mara-app` to `>=2.0.0`


## 1.5.0 (2019-02-13)

- add config option `require_email_http_header` that enforces the presence of the email http header
- Implement previously unimplemented function `currently_user_has_permissions`.
- Implement new function `user_has_permissions`
- Remove functions `user_has_permission` and `current_user_has_permission` (they are now implemented in `mara_page.acl`)
- Remove deprecated dependency_links
- Bump minimum `mara-page` version to 1.4.0
- In `current_user_has_permissions`: When requested for a parent resource, return `True` when permissions for one of the child resources exist 

**required changes**

- In dev environments, add this to `local_setup.py`:

```python
import mara_acl.config

# Disable http header based authentication
patch(mara_acl.config.require_email_http_header)(lambda: False)
```

- Overwrite the default `mara_page.acl` functions like this:

```python
# activate ACL
monkey_patch.patch(mara_page.acl.current_user_email)(mara_acl.users.current_user_email)
monkey_patch.patch(mara_page.acl.current_user_has_permissions)(mara_acl.permissions.current_user_has_permissions)
monkey_patch.patch(mara_page.acl.user_has_permissions)(mara_acl.permissions.user_has_permissions)
```


- If not already the case, add these two dependencies to your project requirements.txt:

```        
-e git+git@github.com:mara/mara-db.git@3.2.1#egg=mara-db
-e git+git@github.com:mara/mara-page.git@1.4.0#egg=mara-page
```


## 1.4.0 (2018-04-08)

- Adapt to changes in mara-db


## 1.3.0 (2018-03-19)

- Replace sqlalchemy orm query logic with plain sql queries in order to avoid idling zombie connections
 

## 1.2.0 (2017-12-30)

- Adapt to changes in the [mara-db](https://github.com/mara/mara-db) package


## 1.1.0 (2017-09-21)

- Adapt to changes in mara ui
- bug fix in invite new user feature



## 1.0.0 - 1.0.4 (2017-03-10) 

- Initial version
- Refactored login 
- Added function `user_has_permission`
- Login bug fix
- Emails are always converted to lowercase before processing
- Adapted to mara ui changes

