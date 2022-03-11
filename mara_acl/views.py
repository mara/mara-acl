"""ACL UI"""

import json

import flask
import mara_db.postgresql
import psycopg2.extensions
from mara_acl import config, keys, permissions, users
from mara_page import acl, navigation, response, bootstrap

blueprint = flask.Blueprint('mara_acl', __name__, static_folder='static', url_prefix='/acl',
                            template_folder='templates')


@blueprint.before_app_first_request
def load_resource_tree():
    config.resources()  # load the tree of resources so that parents / children become linked


acl_resource = acl.AclResource(name='Users', rank=100)


def navigation_entry():
    return navigation.NavigationEntry(
        label='Users & Permissions', uri_fn=lambda: flask.url_for('mara_acl.acl_page'), icon='users', rank=200,
        description='User management, roles & permissions')


@blueprint.route('')
@acl.require_permission(acl_resource)
def acl_page():
    roles = {}

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute(f'SELECT email, role FROM acl_user ORDER BY role')
        for email, role in cursor.fetchall():
            rolekey = keys.user_key(role)
            if not rolekey in roles:
                roles[rolekey] = {'name': role, 'users': {}}
            roles[keys.user_key(role)]['users'][keys.user_key(role, email)] = email

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
                              bootstrap_card=bootstrap.card),
        title='Users, Roles & Permissions',
        js_files=[flask.url_for('mara_acl.static', filename='acl.js')],
        css_files=[flask.url_for('mara_acl.static', filename='acl.css')],
        action_buttons=[
            response.ActionButton('javascript:savePermissions()', 'Save', 'Save permissions', 'save'),
            response.ActionButton('javascript:inviteNewUser()', 'Invite', 'Invite new user', 'plus')
        ])


@blueprint.route('/add-user', methods=['POST'])
@acl.require_permission(acl_resource)
def add_user():
    users.add_user(flask.request.form['email'].strip(), flask.request.form['role'].strip())
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@blueprint.route('/delete-user/<string:email>')
@acl.require_permission(acl_resource)
def deleteuser_handler(email):
    users.delete_user(email)
    flask.flash('Deleted user ' + email, category='success')
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@blueprint.route('/change-user-role/<string:email>/<string:new_role>')
@acl.require_permission(acl_resource)
def change_role(email, new_role):
    users.change_role(email, new_role)
    flask.flash('Changed role of ' + email + ' to ' + new_role, category='success')
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@blueprint.route('/save-permissions', methods=['POST'])
@acl.require_permission(acl_resource)
def save_permissions():
    permissions.save_permissions(json.loads(flask.request.form['permissions']))
    return flask.redirect(flask.url_for('mara_acl.acl_page'))


@blueprint.before_app_request
def login():
    # exclude uris that have been explicitly white listed
    if any(flask.request.path.startswith(uri) for uri in config.whitelisted_uris()):
        return None

    # exclude static folders of blueprints
    if any(flask.request.path.startswith(uri) for uri
           in [blueprint.url_prefix + blueprint.static_url_path
               for blueprint in flask.current_app.blueprints.values()
               if blueprint.static_url_path and blueprint.url_prefix]):
        return None

    result = _handle_login()

    if not isinstance(result, str):
        return result

    email = result
    if not users.login(email):
        flask.abort(403, 'Hi ' + email + ',<br/><br/>We haven\'t created an account for you yet. '
                    + 'Please contact the person that gave you the link this site to fix that.')


def _handle_login() -> str:
    """
    Handles the login process
    
    Returns:
        Null when the page is whiltelisted
        flask.redirect when the page shall be forwareded to a authentication page
        email as str when the user is logged in.
    """

    # get email from header
    email = flask.request.headers.get(config.email_http_header())
    if not email:
        if config.require_email_http_header():
            flask.abort(400, f'HTTP header "{config.email_http_header()}" not set and request URI not whitelisted.')
        else:
            email = 'guest@localhost'

    return email