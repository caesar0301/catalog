# encoding: utf-8
import logging
import logging.config as logging_config

import os
import yaml
from flask import Flask

# Logging utility
logging_conf = os.path.join(os.path.dirname(__file__), 'logging.yml')
if os.path.exists(logging_conf):
    logging_config.dictConfig(yaml.load(open(logging_conf, 'r')))
else:
    print('logging configuration file does not exist')

logger = logging.getLogger(__name__)


def create_app(flask_config_name=None, **kwargs):
    """
    Entry point to the RESTful Server application.
    """
    app = Flask(__name__, **kwargs)

    env_flask_config_name = os.getenv('FLASK_CONFIG')
    if not env_flask_config_name and flask_config_name is None:
        flask_config_name = 'development'
    elif flask_config_name is None:
        flask_config_name = env_flask_config_name
    else:
        if env_flask_config_name:
            assert env_flask_config_name == flask_config_name, (
                    "FLASK_CONFIG environment variable (\"%s\") and flask_config_name argument "
                    "(\"%s\") are both set and are not the same." % (
                        env_flask_config_name,
                        flask_config_name
                    )
            )

    from catalog.config import ProductionConfig
    from catalog.config import DevelopmentConfig
    from catalog.config import TestingConfig

    config_name_mapper = {
        'production': ProductionConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig
    }

    try:
        app.config.from_object(config_name_mapper[flask_config_name])
    except ImportError:
        raise

    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    from catalog import extensions
    from catalog.modules.auth import OAuth2RequestValidator
    kwargs = {
        'oauth_validator': OAuth2RequestValidator
    }
    extensions.init_app(app, **kwargs)

    from . import modules
    modules.init_app(app)

    return app
