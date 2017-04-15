"""ACL UI"""

import json

import flask
from mara_acl import config, keys, permissions, users
from mara_db import dbs
from mara_page import acl, navigation, response

mara_acl = flask.Blueprint('mara_acl', __name__, static_folder='static', url_prefix='/acl', template_folder='templates')

acl_resource = acl.AclResource(name='Users', rank=100)

navigation_entry = navigation.NavigationEntry(
    label='Users & Permissions', uri_fn=lambda: flask.url_for('mara_acl.acl_page'), icon='users', rank=200,
    description='User management, roles & permissions')


@mara_acl.route('')
@acl.require_permission(acl_resource)
def acl_page():
    roles = {}

    with dbs.session_context('mara') as session:  # type: dbs.Session
        for user in session.query(users.User).order_by('role').all():  # type: users.User
            rolekey = keys.user_key(user.role)
            if not rolekey in roles:
                roles[rolekey] = {'name': user.role, 'users': {}}
            roles[keys.user_key(user.role)]['users'][keys.user_key(user.role, user.email)] = user.email

    def resource_tree(name, key, children):
        result = {'name': name, 'key': key, 'children': []}
        for resource in children:  # type: acl.AclResource
            child_key = key + '__' + keys.escape_key(resource.name)
            result['children'].append(resource_tree(resource.name, child_key, resource.children))
        return result

    resources = resource_tree('All', 'resource__All', config.resources())

    return response.Response(
        flask.render_template('acl.html', roles=roles, permissions=permissions.all_permissions(),
                              resources=resources, acl_base_url=flask.url_for('mara_acl.acl_page'),
                              page_top=config.ui_page_top()),
        title='Users, Roles & Permissions',
        js_files=[
            flask.url_for('mara_acl.static', filename='acl.js'),
            flask.url_for('mara_acl.static', filename='jquery.floatThead.min.js')
        ],
        css_files=[
            flask.url_for('mara_acl.static', filename='acl.css')
        ],
        action_buttons=[
            response.ActionButton('javascript:savePermissions()', 'Save', 'Save permissions', 'save'),
            response.ActionButton('javascript:inviteNewUser()', 'Invite', 'Invite new user', 'plus')
        ])


@mara_acl.route('/add-user', methods=['POST'])
@acl.require_permission(acl_resource)
def add_user():
    users.add_user(flask.request.form['email'].strip(), flask.request.form['role'].strip())
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@mara_acl.route('/delete-user/<string:email>')
@acl.require_permission(acl_resource)
def deleteuser_handler(email):
    users.delete_user(email)
    flask.flash('Deleted user ' + email, category='success')
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@mara_acl.route('/change-user-role/<string:email>/<string:new_role>')
@acl.require_permission(acl_resource)
def change_role(email, new_role):
    users.change_role(email, new_role)
    flask.flash('Changed role of ' + email + ' to ' + new_role, category='success')
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@mara_acl.route('/save-permissions', methods=['POST'])
@acl.require_permission(acl_resource)
def save_permissions():
    permissions.save_permissions(json.loads(flask.request.form['permissions']))
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@mara_acl.before_app_request
def login():
    # exclude some uris from login
    if (any(flask.request.path.startswith(uri) for uri in config.whitelisted_uris())):
        return None

    email = flask.request.headers.get(config.email_http_header())
    if not users.login(email if email else 'guest@localhost'):
        flask.abort(403, 'Hi ' + email + ',<br/><br/>We haven\'t created an account for you yet. '
                    + 'Please contact the person that gave you the link this site to fix that.')

