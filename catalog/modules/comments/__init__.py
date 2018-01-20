# encoding: utf-8
from catalog.extensions.api import current_api


def init_app(app, **kwargs):
    current_api.add_oauth_scope('comments:read', "Provide access to comment details")
    current_api.add_oauth_scope('comments:write', "Provide write access to comment details")

    from . import models, resources

    current_api.add_namespace(resources.api)
