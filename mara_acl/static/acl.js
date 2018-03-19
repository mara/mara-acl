// A node in the hiearchy of resources
ResourceNode = function (name, key, parent, children) {
    this.name = name;
    this.key = key;
    this.parent = parent;

    // the level of the node in the tree, counting from top
    this.level = parent ? parent.level + 1 : 0;

    this.childCount = 1; // the number of children, including the node itself
    this.childDepth = 0; // the length of the longest path below the resource

    this.children = [] // all direct children
    if (children) {

        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            var childNode = new ResourceNode(child.name, child.key, this, child.children);
            this.children.push(childNode);
            this.childCount += Math.max(childNode.childCount, 1);
            if (childNode.childDepth + 1 > this.childDepth) {
                this.childDepth = childNode.childDepth + 1;
            }
        }
    }
};

// all resources in a richer tree
var resourceTree = new ResourceNode(resources.name, resources.key, null, resources.children);

// make the top level of resource tree initally visible
resourceTree.visible = true;
resourceTree.children.map(function (resource) {
    resource.visible = true
});

// get a flat list of all resources
var resourcesByKey = {};
(function flattenResourceTree(resource) {
    resourcesByKey[resource.key] = resource;
    for (var resourceKey in resource.children) {
        flattenResourceTree(resource.children[resourceKey]);
    }
})(resourceTree);


// replace current table by something new after each click
function updatePermissionTable() {
    var startTime = new Date().getTime();

    function logTimeSinceStart(label) {
        console.log('' + label + ': ' + (new Date().getTime() - startTime) + 'ms');
    }

    // update resource visibility
    (function updateResourceVisibility(resource) {
        resource.numberOfVisibleChildren = 0;
        resource.children.map(function (child) {
            if (child.visible) {
                resource.numberOfVisibleChildren += 1 + updateResourceVisibility(child);
            }
        });
        return resource.numberOfVisibleChildren;
    })(resourceTree);

    // resources
    var thead = $('<thead/>');

    for (var depth = 1; depth <= resourceTree.childDepth; depth++) { // one header row for each level
        var tr = $('<tr/>').append('<td/>').append('<td>' + (depth == 1 ? 'All' : '') + '</td>');

        for (var key in resourcesByKey) {
            (function () { // need to close on resource
                var resource = resourcesByKey[key];
                var parent = resourcesByKey[resource.parentKey];

                if (resource.level < depth && resource.level > 0 && resource.visible) {
                    tr.append('<td>');
                }

                if (resource.level == depth && resource.visible) {
                    var td = $('<td>').attr('colspan', resource.numberOfVisibleChildren + 1);
                    if (resource.children.length > 0) {
                        td.append(
                            $('<a href="javascript:void(0)">' + (resource.numberOfVisibleChildren > 0 ? '-' : '+') + ' ' + resource.name + '</a>')
                                .click(function () {
                                    toggleResource(resource);
                                }));
                    } else {
                        td.append(resource.name);
                    }
                    tr.append(td);
                }
            })();
        }

        thead.append(tr);
    }

    logTimeSinceStart('head');

    // create cells for permissions
    function permissionCells(roleKey, roleTitle) {
        return Object.keys(resourcesByKey).map(function (resourceKey) {
            var resource = resourcesByKey[resourceKey];
            if (resource.visible) {
                var _class = "not-allowed";
                for (var key in permissions) {
                    var permission = permissions[key];
                    if (permission[0] == roleKey && permission[1] == resourceKey) {
                        // exact match
                        _class = "allowed";
                        break; // stop searching
                    } else if (roleKey.startsWith(permission[0]) && resourceKey.startsWith(permission[1])) {
                        // parent role or resource is allowed
                        _class = "parent-allowed"; // stop searching
                        break;
                    } else if (resourceKey != 'resource__All' && roleKey.startsWith(permission[0]) && permission[1].startsWith(resourceKey)) {
                        // same user / role, with permissions further below in tree
                        _class = "child-allowed";
                        // no break, other cases will override
                    }
                }

                var td = $('<td class="permission" title="' + roleTitle + '&#13;' + resource.name + '"/>').addClass(_class);
                if (_class == 'allowed') {
                    td.click(function () {
                        removePermission(roleKey + '__' + resourceKey);
                    });
                } else if (_class != 'parent-allowed') {
                    td.click(function () {
                        addPermission(roleKey, resourceKey);
                    });
                }
                return td;
            }
        });
    }

    // roles & permissions
    var tbody = $('<tbody/>');
    for (var key in roles) {
        var role = roles[key];
        tbody.append($('<tr class="role"/>').append('<td class="role">' + role.name + '</td>').append(permissionCells(key, role.name)));

        for (var key in role.users) {
            (function () {
                var user = role.users[key];

                var td = $('<td class="user">' + user + ' <a href="' + aclBaseUrl + '/delete-user/'
                    + encodeURIComponent(user) + '" title="Delete user"><span class="fa fa-trash"/></a> </td>');
                var a = $('<a href="javascript:void(0)" title="Change role"><span class="fa fa-pencil"/></a>')
                    .click(function () {
                        $('.user-role-input').remove();
                        var span = $('#user-role-input').clone().addClass('user-role-input');
                        td.append(span.css('display', 'inline-table'));
                        var input = span.children()[0];
                        changeRole = function () {
                            window.location = aclBaseUrl + '/change-user-role/' + encodeURIComponent(user) + '/' + encodeURIComponent($(input).val());
                        };
                        $(input).change(changeRole);
                    });
                td.append(a);

                tbody.append($('<tr class="user"/>').append(td).append(permissionCells(key, user)));
            })();
        }
    }

    logTimeSinceStart('tbody');

    $('#permissions-container').empty().append($('<table class="mara-table table-hover mara-table-float-header">').append(thead).append(tbody));

    if (window.floatMaraTableHeaders()) {
        floatMaraTableHeaders();
    }

    logTimeSinceStart('dom update');
}

$(function () {
    updatePermissionTable();
});


function inviteNewUser() {
    $('#inviteUserModal').modal('toggle');
}

var notSavedWarningHasBeenShown = false;

function showNotSavedWarning() {
    if (!notSavedWarningHasBeenShown) {
        notSavedWarningHasBeenShown = true;
        // showAlert is from the mara_app package. Do nothing if it does not exist
        if (typeof showAlert === "function") {
            showAlert('Permissions have not been saved yet. Please use the "Save" button above to do so.', 'warning');
        }
    }
}


function addPermission(userKey, resourceKey) {
    showNotSavedWarning();
    permissions[userKey + '__' + resourceKey] = [userKey, resourceKey];
    updatePermissionTable();
}

function removePermission(key) {
    showNotSavedWarning();
    delete(permissions[key]);
    updatePermissionTable();
}

function togglePermission(userKey, permissionKey) {
    switch ($('td.' + userKey + '.' + permissionKey + ' > div.permission > div').attr('class')) {
        case 'not-allowed':
        case 'child-allowed':
            if (permissions[userKey]) {
                permissions[userKey].push(permissionKey);
            } else {
                permissions[userKey] = [permissionKey];
            }
            break;
        case 'allowed':
            permissions[userKey].splice(permissions[userKey].indexOf(permissionKey), 1);
            break;
        case 'parent-allowed':
            break;

    }
    updateUI();
}


function savePermissions() {
    $('#permissions-input').val(JSON.stringify(permissions));
    $('#permissions-form').submit();
}

function toggleResource(resource) {
    if (resource.numberOfVisibleChildren > 0) {
        resource.children.map(function collapse(child) {
            child.visible = false;
            child.children.map(collapse);
        });
    } else {
        resource.children.map(function (child) {
            child.visible = true;
        });
    }
    updatePermissionTable();
}