# encoding: utf-8
"""
Flask-RESTplus API registration module
======================================
"""

from flask import Blueprint

from catalog.extensions.api import current_api


def init_app(app, **kwargs):
    blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
    current_api.init_app(blueprint)
    app.register_blueprint(blueprint)
