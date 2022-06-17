User and permission management
==============================

The module provides a single UI for both user and permission management. 
Users can be added / removed and their roles can be changed like this:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/users-and-roles.gif)


Automatic user creation
-----------------------

Each new user that is authenticated is automatically created 
with a default role in the acl:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/automatic-user-creation.png)

This behavior can be switched off (so that only invited users can join). See [config](config.rst) for details.


Managing permissions for users and roles
----------------------------------------

New roles are created by moving a user to a new role.

Permissions can be set for 

- an individual user or a whole role,
- an individual resource, a group of resources or "All" resources.

Individual users inherit permissions from their role, and permissions on higher levels overwrite permissions on lower levels:
![User management](https://github.com/mara/mara-acl/raw/main/docs/_static/permissions.gif)
