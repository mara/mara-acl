"""Acl configuration"""
from mara_page import acl
from mara_config import declare_config


@declare_config()
def resources() -> [acl.AclResource]:
    """All resources that are protected by the acl"""
    return []


@declare_config()
def automatically_create_accounts_for_new_users() -> bool:
    """When true, then a new account is automatically created when a new user tries to login"""
    return True


@declare_config()
def role_for_new_user(is_first_user: bool = False, email: str = 'foo@bar.com') -> str:
    """The role for automatically created users"""
    if is_first_user:
        return 'Admin'
    else:
        return 'Guest'


@declare_config()
def initial_permissions() -> [[str, str]]:
    """The initial permissions that are added when the first user is created"""
    return {'admin_all': ['user__Admin', 'resource__All'],
            'guest_all': ['user__Guest', 'resource__All']}


@declare_config()
def email_http_header() -> str:
    """The http header that contains the email of the authenticated user"""
    return 'X_FORWARDED_EMAIL'


@declare_config()
def whitelisted_uris() -> [str]:
    """Which uris to exclude from the acl"""
    return ['/static/']
