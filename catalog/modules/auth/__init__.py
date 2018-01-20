# encoding: utf-8
"""
Auth module
===========
"""
import logging
from datetime import datetime, timedelta

import sqlalchemy
from flask_login import current_user
from flask_oauthlib import provider

from catalog.extensions import db
from catalog.extensions import login_manager, oauth2
from catalog.extensions.api import current_api
from catalog.modules.auth.models import OAuth2Client, OAuth2Grant, OAuth2Token
from catalog.modules.users.models import User

log = logging.getLogger(__name__)


class OAuth2RequestValidator(provider.OAuth2RequestValidator):
    """
    A project-specific implementation of OAuth2RequestValidator, which connects
    our User and OAuth2* implementations together.
    """

    def __init__(self):
        self._client_class = OAuth2Client
        self._grant_class = OAuth2Grant
        self._token_class = OAuth2Token
        super(OAuth2RequestValidator, self).__init__(
            usergetter=self._usergetter,
            clientgetter=self._client_class.find,
            tokengetter=self._token_class.find,
            grantgetter=self._grant_class.find,
            tokensetter=self._tokensetter,
            grantsetter=self._grantsetter,
        )

    def _usergetter(self, username, password, client, request):
        return User.find_with_password(username, password)

    def _tokensetter(self, token, request, *args, **kwargs):
        # TODO: review expiration time
        expires_in = token['expires_in']
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        try:
            with db.session.begin():
                token_instance = self._token_class(
                    access_token=token['access_token'],
                    refresh_token=token.get('refresh_token'),
                    token_type=token['token_type'],
                    scopes=[scope for scope in token['scope'].split(' ') if scope],
                    expires=expires,
                    client_id=request.client.client_id,
                    user_id=request.user.id,
                )
                db.session.add(token_instance)
        except sqlalchemy.exc.IntegrityError:
            log.exception("Token-setter has failed.")
            return None
        return token_instance

    def _grantsetter(self, client_id, code, request, *args, **kwargs):
        # TODO: review expiration time
        # decide the expires time yourself
        expires = datetime.utcnow() + timedelta(seconds=100)
        try:
            with db.session.begin():
                grant_instance = self._grant_class(
                    client_id=client_id,
                    code=code['code'],
                    redirect_uri=request.redirect_uri,
                    scopes=request.scopes,
                    user=current_user,
                    expires=expires
                )
                db.session.add(grant_instance)
        except sqlalchemy.exc.IntegrityError:
            log.exception("Grant-setter has failed.")
            return None
        return grant_instance


def load_user_from_request(request):
    """
    Load user from OAuth2 Authentication header.
    """
    user = None
    if hasattr(request, 'oauth'):
        user = request.oauth.user
    else:
        is_valid, oauth = oauth2.verify_request(scopes=[])
        if is_valid:
            user = oauth.user
    return user


def init_app(app, **kwargs):
    """
    Init auth module.
    """
    # Bind Flask-Login for current_user
    login_manager.request_loader(load_user_from_request)

    # Register OAuth scopes
    current_api.add_oauth_scope('auth:read', "Provide access to auth details")
    current_api.add_oauth_scope('auth:write', "Provide write access to auth details")

    # Touch underlying modules
    from . import models, views, resources

    # Mount authentication routes
    app.register_blueprint(views.auth_blueprint)
    current_api.add_namespace(resources.api)
