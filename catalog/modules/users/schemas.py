# encoding: utf-8
"""
User schemas
------------
"""

from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import Schema, ModelSchema
from catalog.modules.users.models import User


class UserSchema(ModelSchema):
    """
    Base user schema exposes only the most general fields.
    """

    class Meta:
        model = User
        fields = (
            User.id.key,
            User.username.key,
            User.first_name.key,
            User.middle_name.key,
            User.last_name.key,
            User.followers.key,
            User.following.key,
            User.bio.key,
            User.email.key,
            User.organization.key,
            User.country.key,
            User.github.key,
            User.created.key,
            User.updated.key,
            User.is_active.fget.__name__,
            User.is_regular_user.fget.__name__,
            User.is_admin.fget.__name__,
        )
        dump_only = (
            User.id.key,
            User.created.key,
            User.followers.key,
            User.following.key,
            User.is_active.fget.__name__,
            User.is_regular_user.fget.__name__,
            User.is_admin.fget.__name__,
        )


class UserSignupFormSchema(Schema):
    recaptcha_server_key = base_fields.String(required=True)
