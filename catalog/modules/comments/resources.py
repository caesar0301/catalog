import logging

from catalog.extensions import db
from catalog.extensions import permissions
from catalog.extensions.flask_restplus import Namespace
from catalog.extensions.flask_restplus import Resource
from catalog.modules.comments.models import Comment
from catalog.modules.comments.parameters import UpdateCommentParameters
from catalog.modules.comments.schemas import CommentSchema

log = logging.getLogger(__name__)
api = Namespace('comments', description="On comments")


@api.route('/<comment_id>')
@api.login_required(oauth_scopes=['comments:read'])
@api.resolve_object_by_model(Comment, 'comment', identity_arg_name='comment_id')
class SingleComment(Resource):
    @api.response(CommentSchema())
    def get(self, comment):
        """ Get a specific comment"""
        return comment

    @api.login_required(oauth_scopes=['comments:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['comment']}
    )
    @api.parameters(UpdateCommentParameters())
    @api.response(CommentSchema())
    def patch(self, args, comment):
        """ Update a comment posted by current user"""
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to patch a comment."
        ):
            UpdateCommentParameters.perform_patch(args, comment)
            db.session.merge(comment)
            return comment

    @api.login_required(oauth_scopes=['comments:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['comment']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, comment):
        """ Remove a comment posted by current user"""
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to delete a comment."
        ):
            Comment.delete(comment=comment)
