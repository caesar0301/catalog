# encoding: utf-8
from flask_cors import CORS
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import force_auto_coercion, force_instant_defaults

from . import api
from .auth import OAuth2Provider

cross_origin_resource_sharing = CORS()

force_auto_coercion()
force_instant_defaults()

db = SQLAlchemy(session_options={'autocommit': True})

login_manager = LoginManager()
marshmallow = Marshmallow()

oauth2 = OAuth2Provider()


class AlembicDatabaseMigrationConfig(object):
    """
    Helper config holder that provides missing functions of Flask-Alembic
    package since we use custom invoke tasks instead.
    """

    def __init__(self, database, directory='migrations', **kwargs):
        self.db = database
        self.directory = directory
        self.configure_args = kwargs


def init_app(app, **kwargs):
    """
    Application extensions initialization.
    """
    cross_origin_resource_sharing.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    marshmallow.init_app(app)
    api.init_app(app)
    oauth2.init_app(app, **kwargs)

    app.extensions['migrate'] = AlembicDatabaseMigrationConfig(db, compare_type=True)
