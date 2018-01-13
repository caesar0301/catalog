# encoding: utf-8
"""
Dataset module
============
"""

from catalog.extensions.api import api_v1


def init_app(app, **kwargs):
    """
    Init users module.
    """
    api_v1.add_oauth_scope('datasets:read', "Provide access to dataset details")
    api_v1.add_oauth_scope('datasets:write', "Provide write access to dataset details")

    # Touch underlying modules
    from .resources import dataset, license, organization, publisher, reference, source

    api_v1.add_namespace(dataset.api)
    api_v1.add_namespace(license.api)
    api_v1.add_namespace(organization.api)
    api_v1.add_namespace(publisher.api)
    api_v1.add_namespace(reference.api)
    api_v1.add_namespace(source.api)
