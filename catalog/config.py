import os

from catalog.utils import getenv


class BaseConfig(object):
    SECRET_KEY = getenv('CLOUDSML_API_SERVER_SECRET_KEY', default='this-really-needs-to-be-changed')

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

    DEFAULT_DATABASE_URI = 'sqlite:///%s' % (os.path.join(PROJECT_ROOT, "catalog.db"))
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', default=DEFAULT_DATABASE_URI)

    DEBUG = False
    DASHBOARD_ENABLED = getenv('DASHBOARD_ENABLED', type=bool, default=True)

    ENABLED_MODULES = [
        'landing',
        'auth',
        'users',
        'comments',
        'datasets',
        'stories',
        'api',  # Keep api module as last one for module injection
    ]

    if DASHBOARD_ENABLED:
        ENABLED_MODULES.append('dashboard',)

    AUTHORIZATIONS = {
        'oauth2_password': {
            'type': 'oauth2',
            'flow': 'password',
            'scopes': {},
            'tokenUrl': '/auth/oauth2/token',
        }
        # TODO: implement other grant types for third-party apps
        # 'oauth2_implicit': {
        #    'type': 'oauth2',
        #    'flow': 'implicit',
        #    'scopes': {},
        #    'authorizationUrl': '/auth/oauth2/authorize',
        # },
    }

    # TODO: consider if these are relevant for this project
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CSRF_ENABLED = True

    # See flask_restplus@github issue #142
    SWAGGER_UI_JSONEDITOR = True
    SWAGGER_UI_OAUTH_CLIENT_ID = 'documentation'
    SWAGGER_UI_OAUTH_REALM = "Authentication for server documentation"
    SWAGGER_UI_OAUTH_APP_NAME = "Documentation"


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    # Use in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
