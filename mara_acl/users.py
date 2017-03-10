"""User management"""
import typing
from email.utils import parseaddr

import flask
import sqlalchemy
from mara_acl import config, permissions
from mara_db import dbs
from mara_page import response
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """A user that is known to the ACL"""
    __tablename__ = 'acl_user'

    email = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    role = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, email: str, role: str):
        """
        Creates a new user
        Args:
            email: the email of the user
            role: the role (an arbitrary string) of the user
        """
        self.email = email
        self.role = role
        super().__init__()


def login(email: str) -> typing.Union[response.Response, bool]:
    """Logs in a previously authenticated user. Returns an error response or True upon successful login"""

    # exclude some uris from login
    for uri in config.whitelisted_uris():
        if flask.request.path.startswith(uri): return None

    with dbs.session_context('mara') as session:  # type: dbs.Session
        # get user from db
        user = session.query(User).get(email)  # type: User

        if not user:
            is_first_user = False if session.query(User).first() else True
            print(is_first_user)

            if is_first_user or config.automatically_create_accounts_for_new_users():
                # when first user or when configured, create a new user for a new email
                user = User(email, config.role_for_new_user(is_first_user, email))
                session.add(user)

                # in case this the first login ever, apply default permissions
                if is_first_user:
                    permissions.initialize_permissions()

                flask.flash('Hi <b>' + email + '</b>, we just created a new account for you with the <b>' + user.role
                            + '</b> role. If you need more privileges, please contact the person that invited you.',
                            'info')
            else:
                flask.abort(403, 'Hi ' + email + ',<br/><br/>We haven\'t created an account for you yet. '
                            + 'Please contact the person that gave you the link this site to fix that.')

        # store user in flask g object for later access
        # http://flask.pocoo.org/docs/latest/api/#flask.g
        setattr(flask.g, 'current_user_email', user.email)
        setattr(flask.g, 'current_user_role', user.role)


def current_user_email():
    """the email of the currently logged in user"""
    return getattr(flask.g, 'current_user_email')


def add_user(email: str, role: str):
    """adds a new user"""

    if (not '@' in parseaddr(email)[1]):
        flask.flash('<b>"' + email + '"</b> is not a valid email address', category='warning')
        return

    if not role:
        flask.flash('Could not add <b>"' + email + '"</b>, missing role', category='warning')
        return

    with dbs.session_context('mara') as session:  # type: dbs.Session
        if session.query(User).get(email):
            flask.flash('User <b>"' + email + '"</b> already exists', category='warning')
            return

        session.add(User(email, role))

    flask.flash('Added user "' + email
                + '". No email has been sent, please manually send an invitation via <a href="mailto:'
                + email + '">email</a> or chat.', category='success')


def delete_user(email):
    """deletes a user"""
    with dbs.session_context('mara') as session:  # type: dbs.Session
        session.delete(session.query(User).get(email))


def change_role(email, new_role):
    """sets a new role for a user"""
    with dbs.session_context('mara') as session:  # type: dbs.Session
        user = session.query(User).get(email)  # type: User
        user.role = new_role
