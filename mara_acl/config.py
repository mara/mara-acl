"""Acl configuration"""
from mara_page import acl

def resources() -> [acl.AclResource]:
    """All resources that are protected by the acl"""
    return []


def automatically_create_accounts_for_new_users() -> bool:
    """When true, then a new account is automatically created when a new user tries to login"""
    return True


def role_for_new_user(is_first_user: bool = False, email: str = 'foo@bar.com') -> str:
    """The role for automatically created users"""
    if is_first_user:
        return 'Admin'
    else:
        return 'Guest'


def initial_permissions() -> [[str, str]]:
    """The initial permissions that are added when the first user is created"""
    return {'admin_all': ['user__Admin', 'resource__All'],
            'guest_all': ['user__Guest', 'resource__All']}


def email_http_header() -> str:
    """The http header that contains the email of the authenticated user"""
    return 'X_FORWARDED_EMAIL'


def require_email_http_header() -> str:
    """
    Whether the email http header needs to be present in the request.
    If disabled, then "guest@localhost" will be used.
    Don't disable on production
    """
    return True

def whitelisted_uris() -> [str]:
    """Which uris to exclude from the acl"""
    return []

