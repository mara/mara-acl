"""Maintenance and querying of permissions"""

import flask
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_
from sqlalchemy.ext.declarative import declarative_base

from mara_acl import config, keys, users
from mara_page import acl
import mara_db.sqlalchemy_engine

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

    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        # create a select statement for each resource and combine them with ' UNION ALL '
        queries = [session.query(Permission.query().filter(
            or_(
                Permission.resource_key.like(func.concat(keys.resource_key(resource), '%%')),
                func.concat(keys.resource_key(resource), '%%').like(Permission.resource_key)
            ), Permission.user_key == user_key).exists()) for resource in resources]

        query = None
        for subquery in queries:
            if query is None:
                query = subquery
            else:
                query = query.union_all(subquery)

        return (list(zip(resources, [allowed for (allowed,) in query.all()])))


def user_has_permissions(email: str, resources: [acl.AclResource]) -> [[acl.AclResource, bool]]:
    """Determines whether a user has permissions for a list of resources."""
    email = email.lower()  # make sure always same case is used

    if users.login(email) != True:
        print(f'could not login user "{email}"')
        return [[resource, False] for resource in resources]

    return current_user_has_permissions(resources)


def all_permissions() -> {str: [str, str]}:
    """Returns all currently stored permissions"""
    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        permissions = {}
        for (user_key, resource_key) in session.query(Permission.user_key, Permission.resource_key).all()
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

    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        for new_permission in new_permissions:
            session.insert(Permission).values(user_key=permissions[new_permission][0], resource_key=permissions[new_permission][1])
            
            number_of_changes += 1

        for deleted_permission in deleted_permissions:
            session.delete(Permission).filter(
                Permission.user_key == current_permissions[deleted_permission][0],
                Permission.resource_key == current_permissions[deleted_permission][1])
            number_of_changes += 1

        session.commit()

    if number_of_changes:
        flask.flash('Saved permissions.', category='success')
    else:
        flask.flash('No permission changes', category='warning')


def initialize_permissions():
    """Deletes all existing permissions and adds the configured default permissions"""
    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        session.delete(Permission)
        for user_key, resource_key in config.initial_permissions().values():
            session.insert(Permission).values(user_key=user_key, resource_key=resource_key)

        session.commit()
