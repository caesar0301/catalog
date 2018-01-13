# encoding: utf-8
"""
Users module
============
"""
from catalog.extensions.api import api_v1


def init_app(app, **kwargs):
    """
    Init users module.
    """
    api_v1.add_oauth_scope('users:read', "Provide access to user details")
    api_v1.add_oauth_scope('users:write', "Provide write access to user details")

    # Touch underlying modules
    from . import models, resources

    api_v1.add_namespace(resources.api)
