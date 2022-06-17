"""Make the functionalities of this package auto-discoverable by mara-app"""
__version__ = '2.1.0'


def MARA_CONFIG_MODULES():
    from . import config
    return [config]


def MARA_FLASK_BLUEPRINTS():
    from . import views
    return [views.blueprint]


def MARA_AUTOMIGRATE_SQLALCHEMY_MODELS():
    from . import permissions, users
    return [permissions.Permission, users.User]


def MARA_ACL_RESOURCES():
    from . import views
    return {'Acl': views.acl_resource}


def MARA_CLICK_COMMANDS():
    return []


def MARA_NAVIGATION_ENTRIES():
    from . import views
    return {'Acl': views.navigation_entry()}
