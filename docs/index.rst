.. rst-class:: hide-header

Mara ACL documentation
======================

Welcome to Mara ACL’s documentation. This is one of the core modules of the `Mara Framework <https://github.com/mara>`_
offering simple ACL user permission management.

It uses a simple design:

* Authentication of users is handled externally, e.g. through a `OAuth2 Proxy <https://github.com/oauth2-proxy/oauth2-proxy>`_. An upstream authentication app manages authentication and then adds a http header identifying the user to each authenticated request.
* Each user is assigned a single role.
* Permissions are not based on urls, but on application-defined "resources". Thus, checking of permissions needs to be done in the application.


User's Guide
------------

This part of the documentation focuses on step-by-step instructions how to use this extension.

.. toctree::
   :maxdepth: 2

   installation
   authentication
   user-and-permission-management
   config


Additional Notes
----------------

Legal information and changelog are here for the interested.

.. toctree::
   :maxdepth: 2

   license
   changes
