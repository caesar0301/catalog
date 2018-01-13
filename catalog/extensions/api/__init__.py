# encoding: utf-8
"""
API extension
=============
"""

from copy import deepcopy

from .api import Api
from .http_exceptions import abort
from .namespace import Namespace

api_v1 = Api(
    version='1.0',
    title="Prism API",
    description=(
        "It is a [registry service](http://github.com/caesar0301/prism) endeavoring to "
        "index world-wide data sources.\n"
    ),
)


def serve_swaggerui_assets(path):
    """
    Swagger-UI assets serving route.
    """
    from flask import send_from_directory
    from flask import current_app as app
    if not app.debug:
        import warnings
        warnings.warn(
            "/swaggerui/ is recommended to be served by public-facing server (e.g. NGINX)"
        )
    return send_from_directory(app.config['STATIC_ROOT'], path)


def init_app(app, **kwargs):
    """
    API extension initialization point.
    """
    app.route('/swaggerui/<path:path>')(serve_swaggerui_assets)

    # Prevent config variable modification with runtime changes
    api_v1.authorizations = deepcopy(app.config['AUTHORIZATIONS'])
