"""User management"""
import typing
from email.utils import parseaddr
import flask
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from mara_acl import config, permissions
from mara_page import response
import mara_db.sqlalchemy_engine

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
    email = email.lower()  # make sure always same case is used

    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        # get user from db
        result = session.query(User.email, User.role).filter(User.email == email).first()

        if not result:
            is_first_user = not session.query(User.query().exists()).scalar()

            if is_first_user or config.automatically_create_accounts_for_new_users():
                role = config.role_for_new_user(is_first_user, email)
                # when first user or when configured, create a new user for a new email
                session.insert(User).values(email=email, role=role)
                session.commit()

                # in case this the first login ever, apply default permissions
                if is_first_user:
                    permissions.initialize_permissions()

                flask.flash('Hi <b>' + email + '</b>, we just created a new account for you with the <b>' + role
                            + '</b> role. If you need more privileges, please contact the person that invited you.',
                            'info')
            else:
                return False
        else:
            email, role = result

        # store user in flask g object for later access
        # http://flask.pocoo.org/docs/latest/api/#flask.g
        setattr(flask.g, 'current_user_email', email)
        setattr(flask.g, 'current_user_role', role)
        return True


def current_user_email():
    """the email of the currently logged in user"""
    return getattr(flask.g, 'current_user_email')


def current_user_role():
    """the role of the currently logged in user"""
    return getattr(flask.g, 'current_user_role')


def add_user(email: str, role: str):
    """adds a new user"""
    email = email.lower()  # make sure always same case is used

    if not '@' in parseaddr(email)[1]:
        flask.flash('<b>"' + email + '"</b> is not a valid email address', category='warning')
        return

    if not role:
        flask.flash('Could not add <b>"' + email + '"</b>, missing role', category='warning')
        return

    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        # get user from db
        if session.query(User.query().filter(User.email == email).exists()).scalar():
            flask.flash('User <b>"' + email + '"</b> already exists', category='warning')
            return

        session.insert(User).values(email=email, role=role)
        session.commit()

    flask.flash('Added user "' + email
                + '". No email has been sent, please manually send an invitation via <a href=\'mailto:'
                + email + '\'>email</a> or chat.', category='success')


def delete_user(email):
    """deletes a user"""
    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        session.delete(User).filter(User.email == email)
        session.commit()


def change_role(email, new_role):
    """sets a new role for a user"""
    Session = sessionmaker(bind=mara_db.sqlalchemy_engine.engine('mara'))
    with Session() as session:
        session.update(User).where(User.email == email).values(User.role == new_role)
        session.commit()
