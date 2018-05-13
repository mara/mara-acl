
def MARA_CONFIG_MODULES():
    from mara_acl import config
    return [config]


def MARA_FLASK_BLUEPRINTS():
    from mara_acl import views
    return [views.blueprint]


def MARA_AUTOMIGRATE_SQLALCHEMY_MODELS():
    from mara_acl import permissions, users
    return [permissions.Permission, users.User]


def MARA_ACL_RESOURCES():
    from mara_acl import views
    return [views.acl_resource]


def MARA_NAVIGATION_ENTRY_FNS():
    from mara_acl import views
    return [views.navigation_entry]
