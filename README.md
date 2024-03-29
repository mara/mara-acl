# Mara ACL

[![mara-acl](https://github.com/mara/mara-acl/actions/workflows/build.yaml/badge.svg)](https://github.com/mara/mara-page/actions/workflows/build.yaml)
[![PyPI - License](https://img.shields.io/pypi/l/mara-acl.svg)](https://github.com/mara/mara-acl/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/mara-acl.svg)](https://badge.fury.io/py/mara-acl)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://communityinviter.com/apps/mara-users/public-invite)

Default ACL implementation for mara with the following design choices:

- Authentication of users is handled externally, e.g. through a [OAuth2 Proxy](https://github.com/oauth2-proxy/oauth2-proxy).
  An upstream authentication app manages authentication and then adds a http header identifying the user to each authenticated request.
- Each user is assigned a single role.
- Permissions are not based on urls, but on application-defined "resources".
  Thus, checking of permissions needs to be done in the application.

The ACL provides a single UI for both user and permission management.
Users can be added / removed and their roles can be changed like this:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/users-and-roles.gif)

New roles are created by moving a user to a new role.

Permissions can be set for

- an individual user or a whole role,
- an individual resource, a group of resources or "All" resources.

Individual users inherit permissions from their role, and permissions on higher levels overwrite permissions on lower levels:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/permissions.gif)


Each new user that is authenticated is automatically created
with a default role in the acl:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/automatic-user-creation.png)

This behavior can be switched off (so that only invited users can join). See [config.py](https://github.com/mara/mara-acl/blob/main/mara_acl/config.py) for details.


Please have a look at the mara example application for how to integrate this ACL implementation.


## Links

* Documentation: https://mara-acl.readthedocs.io/
* Changes: https://mara-acl.readthedocs.io/en/stable/changes.html
* PyPI Releases: https://pypi.org/project/mara-acl/
* Source Code: https://github.com/mara/mara-acl
* Issue Tracker: https://github.com/mara/mara-acl/issues/
