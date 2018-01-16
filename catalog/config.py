import os


class BaseConfig(object):
    SECRET_KEY = os.getenv('CLOUDSML_API_SERVER_SECRET_KEY', 'this-really-needs-to-be-changed')

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

    DEFAULT_DATABASE_URI = 'sqlite:///%s' % (os.path.join(PROJECT_ROOT, "catalog.db"))
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', DEFAULT_DATABASE_URI)

    DEBUG = False

    ENABLED_MODULES = (
        'auth',
        'users',
        'comments',
        'datasets',
        'events',
        'stories',
        # Keep api module as last one for module injection
        'api'
    )

    AUTHORIZATIONS = {
        'oauth2_password': {
            'type': 'oauth2',
            'flow': 'password',
            'scopes': {},
            'tokenUrl': '/auth/oauth2/token',
        }
    }

    SWAGGER_UI_JSONEDITOR = True
    SWAGGER_UI_OAUTH_CLIENT_ID = 'documentation'
    SWAGGER_UI_OAUTH_REALM = "Authentication for Catalog server documentation"
    SWAGGER_UI_OAUTH_APP_NAME = "Catalog server documentation"

    # TODO: consider if these are relevant for this project
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CSRF_ENABLED = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    # Use in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
