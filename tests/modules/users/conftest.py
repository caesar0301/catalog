# encoding: utf-8
import pytest
from flask_login import current_user, login_user, logout_user

from catalog.modules.users import models
from tests import utils


@pytest.fixture()
def patch_User_password_scheme():
    """
    By default, the application uses ``bcrypt`` to store passwords securely.
    However, ``bcrypt`` is a slow hashing algorithm (by design), so it is
    better to downgrade it to ``plaintext`` while testing, since it will save
    us quite some time.
    """
    # NOTE: It seems a hacky way, but monkeypatching is a hack anyway.
    password_field_context_config = models.User.password.property.columns[0].type.context._config
    if password_field_context_config is not None:
        password_field_context_config._init_scheme_list(('plaintext',))
        password_field_context_config._init_records()
        password_field_context_config._init_default_schemes()
        yield
        password_field_context_config._init_scheme_list(('bcrypt',))
        password_field_context_config._init_records()
        password_field_context_config._init_default_schemes()
    else:
        yield  # in case that the context._config is None (maybe caused by weakref, By Xiaming)


@pytest.fixture()
def user_instance(patch_User_password_scheme):
    user_id = 1
    _user_instance = utils.generate_user_instance(user_id=user_id)
    _user_instance.get_id = lambda: user_id
    return _user_instance


@pytest.fixture()
def authenticated_user_instance(flask_app, user_instance):
    with flask_app.test_request_context('/'):
        login_user(user_instance)
        yield current_user
        logout_user()


@pytest.fixture()
def anonymous_user_instance(flask_app):
    with flask_app.test_request_context('/'):
        yield current_user
