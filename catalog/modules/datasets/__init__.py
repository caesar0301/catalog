# encoding: utf-8
"""
Dataset module
============
"""

from catalog.extensions.api import current_api


def init_app(app, **kwargs):
    """
    Init users module.
    """
    current_api.add_oauth_scope('datasets:read', "Provide access to dataset details")
    current_api.add_oauth_scope('datasets:write', "Provide write access to dataset details")

    # Touch underlying modules
    from .resources import dataset, license, organization, publisher, reference, source

    current_api.add_namespace(dataset.api)
    current_api.add_namespace(license.api)
    current_api.add_namespace(organization.api)
    current_api.add_namespace(publisher.api)
    current_api.add_namespace(reference.api)
    current_api.add_namespace(source.api)
