"""Maintenance and querying of permissions"""

import flask
import sqlalchemy
import sqlalchemy.ext.declarative
from mara_acl import config, keys
from mara_db import dbs
from mara_page import acl
from sqlalchemy.ext.declarative import declarative_base

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

    def key(self) -> str:
        return self.user_key + '__' + self.resource_key


def current_user_has_permission(resource: acl.AclResource) -> bool:
    """Returns whether the current user is allowed to access a specific resource"""
    with dbs.session_context('mara') as session:  # type: dbs.Session
        if session.execute("SELECT EXISTS (SELECT 1 FROM acl_permission WHERE '"
                                   + keys.resource_key(resource) + "' LIKE CONCAT(resource_key,'%') AND '"
                                   + keys.user_key(getattr(flask.g, 'current_user_role'),
                                                   getattr(flask.g, 'current_user_email'))
                                   + "' LIKE CONCAT(user_key,'%'))").scalar():
            return True
        else:
            return False


def current_user_has_permissions(resources: [acl.AclResource]) -> [[acl.AclResource, bool]]:
    """Determines whether the currently logged in user has permissions for a list of resources"""
    return map(lambda resource: [resource, True], resources)


def all_permissions() -> {str: [str, str]}:
    """Returns all currently stored permissions"""
    with dbs.session_context('mara') as session:  # type: dbs.Session
        permissions = {}
        for permission in session.query(Permission).all():  # type: Permission
            permissions[permission.key()] = [permission.user_key, permission.resource_key]
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

    number_of_changes = 0;

    with dbs.session_context('mara') as session:  # type: dbs.Session
        for new_permission in new_permissions:
            session.add(Permission(permissions[new_permission][0], permissions[new_permission][1]))
            number_of_changes += 1

        for deleted_permission in deleted_permissions:
            session.delete(session.query(Permission)
                           .filter(Permission.user_key == current_permissions[deleted_permission][0])
                           .filter(Permission.resource_key == current_permissions[deleted_permission][1])
                           .first())
            number_of_changes += 1

    if number_of_changes:
        flask.flash('Saved permissions.', category='success')
    else:
        flask.flash('No permission changes', category='warning')


def initialize_permissions():
    """Deletes all existing permissions and adds the configured default permissions"""
    with dbs.session_context('mara') as session:  # type: dbs.Session
        session.query(Permission).delete()
        session.commit()
        save_permissions(config.initial_permissions())
