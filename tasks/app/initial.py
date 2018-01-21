# encoding: utf-8
"""
This file contains initialization data for development usage only.

You can execute this code via ``invoke app.db.init_dev_data``
"""
import os
import yaml

from catalog.extensions import db, api
from catalog.modules.auth.models import OAuth2Client
from catalog.modules.datasets.models import Dataset
from catalog.modules.users.models import User
from tasks.settings import Settings


def init_users():
    with db.session.begin():
        root_user = User(
            username='root',
            email='root@localhost',
            password='q',
            is_active=True,
            is_regular_user=True,
            is_admin=True
        )
        db.session.add(root_user)
        docs_user = User(
            username='catalog',
            email='catalog@localhost',
            password='w',
            is_active=True
        )
        db.session.add(docs_user)
        regular_user = User(
            username='user',
            email='user@localhost',
            password='w',
            is_active=True,
            is_regular_user=True
        )
        db.session.add(regular_user)
        internal_user = User(
            username='internal',
            email='internal@localhost',
            password='q',
            is_active=True,
            is_internal=True
        )
        db.session.add(internal_user)
    return root_user, docs_user, regular_user


def init_auth(user):
    # TODO: OpenAPI documentation has to have OAuth2 Implicit Flow instead
    # of Resource Owner Password Credentials Flow
    with db.session.begin():
        oauth2_client = OAuth2Client(
            client_id=Settings.CATALOG_CLIENT_ID,
            client_secret=Settings.CATALOG_CLIENT_SECRET,
            user_id=user.id,
            redirect_uris=[],
            default_scopes=api.api_v1.authorizations['oauth2_password']['scopes']
        )
        db.session.add(oauth2_client)
    return oauth2_client


def init_datasets(user):
    data_file = open(os.path.join(os.path.dirname(__file__), 'data/datasets.yml'))
    datasets = yaml.load(data_file)['datasets']
    with db.session.begin():
        for data_desc in datasets:
            Dataset.create(contributor=user, **data_desc)


def init():
    # Automatically update `default_scopes` for `documentation` OAuth2 Client,
    # as it is nice to have an ability to evaluate all available API calls.
    with db.session.begin():
        OAuth2Client.query.filter(OAuth2Client.client_id == 'documentation').update({
            OAuth2Client.default_scopes: api.api_v1.authorizations['oauth2_password']['scopes'],
        })

    assert User.query.count() == 0, \
        "Database is not empty. You should not re-apply fixtures! Aborted."

    root_user, docs_user, regular_user = init_users()  # pylint: disable=unused-variable
    init_auth(docs_user)
    # init_datasets(docs_user)
