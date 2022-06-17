Authentication
==============

The authentication process is handled externally. By default, an upstream authentication app manages authentication and then adds a http header identifying the user to each authenticated request.

OAuth2 proxy
------------

See [OAuth2 Proxy Docs](https://oauth2-proxy.github.io/oauth2-proxy/docs/) how to install and configure it.

Make sure that the E-Mail address of the user account is passed to the app and make sure that the HTTP header is correctly configured in [`mara_acl.config.email_http_header`](config.rst).

Microsoft MSAL
--------------

When you want to use Microsoft authentication via the [Microsoft MSAL](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview) library you have the additional option to use the extension [Mara ACL MSAL](https://github.com/leo-schick/mara-acl-msal). Take a look at the GitHub repository readme for more information.
