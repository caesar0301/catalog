# encoding: utf-8
"""
RESTful API User resources
--------------------------
"""

import logging
from http import HTTPStatus

from flask_login import current_user

from catalog.extensions import permissions
from catalog.extensions.flask_restplus import Namespace
from catalog.extensions.flask_restplus import Resource
from catalog.extensions.flask_restplus.parameters import PaginationParameters
from catalog.modules.comments.schemas import CommentSchema
from catalog.modules.datasets.schemas import DatasetSchema, ReferenceSchema, \
    SourceSchema, LicenseSchema, OrganizationSchema, PublisherSchema
from catalog.modules.stories.schemas import StorySchema
from catalog.modules.users import schemas, parameters
from catalog.modules.users.models import db, User

log = logging.getLogger(__name__)
api = Namespace('users', description="Users")


@api.route('/')
class Users(Resource):
    """
    Manipulations with users.
    """

    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.AdminRolePermission())
    @api.parameters(PaginationParameters())
    @api.response(schemas.UserSchema(many=True))
    def get(self, args):
        """
        List of all users.

        Returns a list of users starting from ``offset`` limited by ``limit``
        parameter.
        """
        return User.query.offset(args['offset']).limit(args['limit'])

    @api.parameters(parameters.AddUserParameters())
    @api.response(schemas.UserSchema())
    @api.doc(id='create_user')
    def post(self, args):
        """
        Create a new user.
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to create a new user."
        ):
            new_user = User(**args)
            db.session.add(new_user)
        return new_user


@api.route('/signup_form')
class UserSignupForm(Resource):
    @api.response(schemas.UserSignupFormSchema())
    def get(self):
        """
        Get signup form keys.

        This endpoint must be used in order to get a server reCAPTCHA public key which
        must be used to receive a reCAPTCHA secret key for POST /users/ form.
        """
        # TODO:
        return {"recaptcha_server_key": "TODO"}


@api.route('/<int:id>')
@api.login_required(oauth_scopes=['users:read'])
@api.response(
    code=HTTPStatus.NOT_FOUND,
    description="User not found.",
)
@api.resolve_object_by_model(User, 'user', identity_arg_name='id')
class UserByID(Resource):
    """
    Manipulations with a specific user.
    """

    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['user']}
    )
    @api.response(schemas.UserSchema())
    def get(self, user):
        """
        Get user details by ID.
        """
        return user

    @api.login_required(oauth_scopes=['users:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['user']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.parameters(parameters.PatchUserDetailsParameters())
    @api.response(schemas.UserSchema())
    def patch(self, args, user):
        """
        Patch user details by ID.
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to update user details."
        ):
            parameters.PatchUserDetailsParameters.perform_patch(args, user)
            db.session.merge(user)
        return user


@api.route('/me')
@api.login_required(oauth_scopes=['users:read'])
class UserMe(Resource):
    """
    Useful reference to the authenticated user itself.
    """

    @api.response(schemas.UserSchema())
    def get(self):
        """
        Get current user details.
        """
        return User.query.get_or_404(current_user.id)


@api.route('/followers')
class UserAllFollowers(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.parameters(PaginationParameters())
    @api.response(schemas.UserSchema(many=True))
    def get(self, args):
        """Get all followers of current user
        """
        return User.query_all_followers(current_user.id) \
            .offset(args['offset']).limit(args['limit'])


@api.route('/following')
class UserAllFollowing(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.parameters(PaginationParameters())
    @api.response(schemas.UserSchema(many=True))
    def get(self, args):
        """Get all following users of current user
        """
        return User.query_all_following(current_user.id) \
            .offset(args['offset']).limit(args['limit'])


@api.route('/following/<int:uid>')
class UserFollowingUpdate(Resource):
    @api.login_required(oauth_scopes=['users:write'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(schemas.UserSchema())
    def patch(self, uid):
        """Follow a new user
        """
        # TODO: do not follow himself
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to update following relationships"
        ):
            user = User.query.get_or_404(current_user.id)
            user.follows(uid)
        return user

    @api.login_required(oauth_scopes=['users:write'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(schemas.UserSchema())
    def delete(self, uid):
        """Un-follow a user
        """
        # TODO: do not follow himself
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to update following relationships"
        ):
            user = User.query.get_or_404(current_user.id)
            user.unfollows(uid)
        return user


@api.route('/comments')
class UserComments(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(CommentSchema(many=True))
    def get(self):
        """ Get all comments posted by current user"""
        return current_user.comments


@api.route("/datasets")
class UserDatasets(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(DatasetSchema(many=True))
    def get(self):
        """ Get all datasets added by current user"""
        return current_user.datasets


@api.route("/references")
class UserReferences(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(ReferenceSchema(many=True))
    def get(self):
        """ Get all references posted by current user"""
        pass


@api.route("/sources")
class UserSources(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(SourceSchema(many=True))
    def get(self):
        """ Get all data sources posted by current user"""
        pass


@api.route("/licenses")
class UserLicenses(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(LicenseSchema(many=True))
    def get(self):
        """ Get all licenses posted by current user"""
        pass


@api.route("/organizations")
class UserOrgs(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(OrganizationSchema(many=True))
    def get(self):
        """ Get all organizations posted by current user"""
        pass


@api.route("/publishers")
class UserPublishers(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(PublisherSchema(many=True))
    def get(self):
        """ Get all publishers posted by current user"""
        pass


@api.route("/stories")
class UserStories(Resource):
    @api.login_required(oauth_scopes=['users:read'])
    @api.permission_required(permissions.OwnerRolePermission())
    @api.response(StorySchema(many=True))
    def get(self):
        """ Get all stories added by current user"""
        return current_user.stories
