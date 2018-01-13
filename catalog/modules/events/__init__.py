# encoding: utf-8
from catalog.extensions.api import api_v1

def init_app(app, **kwargs):
    from . import models

    # api_v1.add_oauth_scope('events:read', "Provide access to event details")
    # api_v1.add_oauth_scope('events:write', "Provide write access to event details")
