"""Unique identifiers for users, roles, resources & permissions"""

from mara_page import acl


def escape_key(string: str) -> str:
    """Removes all characters from a string that are not allowed in css classes"""
    return string.translate({ord(c): '-' for c in
                             [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':',
                              ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '`', '{', '|', '}', '~']})


def user_key(role: str, email: str = None) -> str:
    """Computes a unique key for a user or a role"""
    return escape_key('user__' + role + ('__' + email if email else ''))


def resource_key(resource: acl.AclResource) -> str:
    """Computes a unique key for a permission"""
    return (resource_key(resource.parent) if resource.parent else 'resource__All') \
           + '__' + escape_key(resource.name)

