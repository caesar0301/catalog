# encoding: utf-8
from catalog.extensions.api import api_v1


def init_app(app, **kwargs):
    """
    Init users module.
    """
    # Touch underlying modules
    from . import models, resources

    api_v1.add_oauth_scope('stories:read', "Provide access to data story details")
    api_v1.add_oauth_scope('stories:write', "Provide write access to data story details")

    api_v1.add_namespace(resources.api)
