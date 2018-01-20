# encoding: utf-8
"""
Users module
============
"""
from catalog.extensions.api import current_api


def init_app(app, **kwargs):
    """
    Init users module.
    """
    current_api.add_oauth_scope('users:read', "Provide access to user details")
    current_api.add_oauth_scope('users:write', "Provide write access to user details")

    # Touch underlying modules
    from . import models, resources

    current_api.add_namespace(resources.api)
