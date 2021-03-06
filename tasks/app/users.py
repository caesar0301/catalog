# encoding: utf-8
"""
Application Users management related tasks for Invoke.
"""

from ._utils import app_context_task


@app_context_task(help={'username': "qwe"})
def create(
        context,
        username,
        email,
        is_internal=False,
        is_admin=False,
        is_regular_user=True,
        is_active=True
):
    """
    Create a new user.
    """
    from catalog.modules.users.models import User

    password = input("Enter password: ")

    new_user = User(
        username=username,
        password=password,
        email=email,
        is_internal=is_internal,
        is_admin=is_admin,
        is_regular_user=is_regular_user,
        is_active=is_active
    )

    from catalog.extensions import db
    db.session.add(new_user)
    db.session.commit()


@app_context_task
def create_oauth2_client(
        context,
        username,
        client_id,
        client_secret,
        default_scopes=None
):
    """
    Create a new OAuth2 Client associated with a given user (username).
    """
    from catalog.modules.users.models import User
    from catalog.modules.auth.models import OAuth2Client

    user = User.query.first(User.username == username)
    if not user:
        raise Exception("User with username '%s' does not exist." % username)

    if default_scopes is None:
        from catalog.extensions.api import api_v1
        default_scopes = ' '.join(api_v1.authorizations['oauth2_password']['scopes'])

    oauth2_client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        user=user,
        _default_scopes=default_scopes
    )

    from catalog.extensions import db
    db.session.add(oauth2_client)
    db.session.commit()
