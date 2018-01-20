# encoding: utf-8
from catalog.extensions.api import current_api


def init_app(app, **kwargs):
    """
    Init users module.
    """
    # Touch underlying modules
    from . import models, resources

    current_api.add_oauth_scope('stories:read', "Provide access to data story details")
    current_api.add_oauth_scope('stories:write', "Provide write access to data story details")

    current_api.add_namespace(resources.api)
