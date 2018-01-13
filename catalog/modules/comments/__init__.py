# encoding: utf-8
from catalog.extensions.api import api_v1


def init_app(app, **kwargs):
    api_v1.add_oauth_scope('comments:read', "Provide access to comment details")
    api_v1.add_oauth_scope('comments:write', "Provide write access to comment details")

    from . import models, resources

    api_v1.add_namespace(resources.api)
