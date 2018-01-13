# encoding: utf-8
"""
OAuth2 provider setup.

It is based on the code from the example:
https://github.com/lepture/example-oauth2-server

More details are available here:
* http://flask-oauthlib.readthedocs.org/en/latest/oauth2.html
* http://lepture.com/en/2013/create-oauth-server
"""
from http import HTTPStatus

from flask_oauthlib import provider

from .. import api

__all__ = ['OAuth2Provider']


def api_invalid_response(req):
    """
    This is a default handler for OAuth2Provider, which raises abort exception
    with error message in JSON format.
    """
    api.abort(code=HTTPStatus.UNAUTHORIZED.value)


class OAuth2Provider(provider.OAuth2Provider):
    """
    A helper class which connects OAuth2RequestValidator with OAuth2Provider.
    """

    def __init__(self, *args, **kwargs):
        super(OAuth2Provider, self).__init__(*args, **kwargs)
        self.invalid_response(api_invalid_response)

    def init_app(self, app, **kwargs):
        super(OAuth2Provider, self).init_app(app)
        # Set user-defined oauth2 validator
        validator = kwargs.pop('oauth_validator', None)
        if validator:
            self._validator = validator()
