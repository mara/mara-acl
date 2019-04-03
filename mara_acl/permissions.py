"""Maintenance and querying of permissions"""

import flask
import psycopg2.extensions
import psycopg2.extras
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

import mara_db.postgresql
from mara_acl import config, keys, users
from mara_page import acl

Base = declarative_base()


class Permission(Base):
    """Maps a role or user to a resource or a group of resources"""
    __tablename__ = 'acl_permission'
    user_key = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    resource_key = sqlalchemy.Column(sqlalchemy.String, primary_key=True)

    def __init__(self, user_key, resource_key):
        self.user_key = user_key
        self.resource_key = resource_key
        super().__init__()



def current_user_has_permissions(resources: [acl.AclResource]) -> [[acl.AclResource, bool]]:
    """Determines whether the currently logged in user has permissions for a list of resources"""
    user_key = keys.user_key(getattr(flask.g, 'current_user_role'), getattr(flask.g, 'current_user_email'))

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        # create a select statement for each resource and combine them with ' UNION ALL '
        cursor.execute(' UNION ALL '.join([
            cursor.mogrify(f"""
SELECT EXISTS (SELECT 1 FROM acl_permission 
               WHERE ({'%s'} LIKE CONCAT(resource_key, '%%') OR resource_key LIKE CONCAT({'%s'}, '%%')) 
                   AND {'%s'} LIKE CONCAT(user_key,'%%'))
""",
                           (keys.resource_key(resource), keys.resource_key(resource), user_key)).decode("utf-8")
            for resource in resources]))

        return (list(zip(resources, [allowed for (allowed,) in cursor.fetchall()])))


def user_has_permissions(email: str, resources: [acl.AclResource]) -> [[acl.AclResource, bool]]:
    """Determines whether a user has permissions for a list of resources."""
    email = email.lower()  # make sure always same case is used

    if users.login(email) != True:
        print(f'could not login user "{email}"')
        return [[resource, False] for resource in resources]

    return current_user_has_permissions(resources)


def all_permissions() -> {str: [str, str]}:
    """Returns all currently stored permissions"""
    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute("SELECT user_key, resource_key FROM acl_permission")
        permissions = {}
        for (user_key, resource_key) in cursor.fetchall():
            permissions[user_key + '__' + resource_key] = [user_key, resource_key]
        return permissions


def save_permissions(permissions: {str: [str, str]}):
    """
    Saves a set of permissions
    Args:
        permissions: a dictionary in the form {'user_key1__permission_key1': ['user_key1', 'permission_key1'],
                                               'user_key2__permission_key2': ['user_key2', 'permission_key2']}
    """
    current_permissions = all_permissions()
    new_permissions = list(set(permissions) - set(current_permissions))
    deleted_permissions = list(set(current_permissions) - set(permissions))

    number_of_changes = 0

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        for new_permission in new_permissions:
            cursor.execute(f"INSERT INTO acl_permission (user_key, resource_key) VALUES ({'%s, %s'})",
                           (permissions[new_permission][0], permissions[new_permission][1]))
            number_of_changes += 1

        for deleted_permission in deleted_permissions:
            cursor.execute(f"DELETE FROM acl_permission WHERE user_key = {'%s'} AND resource_key = {'%s'}",
                           (current_permissions[deleted_permission][0], current_permissions[deleted_permission][1]))
            number_of_changes += 1

    if number_of_changes:
        flask.flash('Saved permissions.', category='success')
    else:
        flask.flash('No permission changes', category='warning')


def initialize_permissions():
    """Deletes all existing permissions and adds the configured default permissions"""
    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute('TRUNCATE acl_permission')
        for user_key, resource_key in config.initial_permissions().values():
            cursor.execute(f"INSERT INTO acl_permission (user_key, resource_key) VALUES ({'%s, %s'})",
                           (user_key, resource_key))
