# encoding: utf-8
"""
RESTful API for Story resource
--------------------------
"""
import logging

from catalog.extensions import db
from catalog.extensions import permissions
from catalog.extensions.api import Namespace
from catalog.extensions.api.parameters import PaginationParameters
from catalog.extensions.flask_restplus import Resource
from catalog.modules.comments.models import Comment, CommentType
from catalog.modules.comments.parameters import AddCommentParameters
from catalog.modules.comments.schemas import CommentSchema
from catalog.modules.stories.models import Story
from catalog.modules.stories.parameters import UpdateStoryParameters
from catalog.modules.stories.schemas import StorySchema
from catalog.modules.users.models import User, UserStarStory

log = logging.getLogger(__name__)
api = Namespace('stories', description="On stories")


@api.route('/')
@api.login_required(oauth_scopes=['stories:read'])
class StoryResource(Resource):
    @api.parameters(PaginationParameters())
    @api.response(StorySchema(many=True))
    def get(self, args):
        """
        List of all stories.

        :param args: query parameters
        :return: a list of stories starting from ``offset`` limited by
        ``limit`` parameter.
        """
        return Story.query.offset(args['offset']).limit(args['limit'])


@api.route('/<story_id>')
@api.login_required(oauth_scopes=['stories:read'])
@api.resolve_object_by_model(Story, 'story', identity_arg_name='story_id')
class SingleStory(Resource):
    @api.response(StorySchema())
    def get(self, story_id):
        """ Get details of a story"""
        return Story.get(story_id=story_id)

    @api.login_required(oauth_scopes=['stories:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['story']}
    )
    @api.parameters(UpdateStoryParameters())
    @api.response(StorySchema())
    def patch(self, args, story_id):
        """ Update a story"""
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to patch a story."
        ):
            Story.query.filter_by(id=story_id).update(dict(args))
            return Story.get(story_id=story_id)

    @api.login_required(oauth_scopes=['stories:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['story']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, story_id):
        """ Delete a specifici story (TODO)"""
        pass


@api.route('/<story_id>/stars')
@api.login_required(oauth_scopes=['stories:read'])
class StarStoryAction(Resource):
    @api.login_required(oauth_scopes=['stories:write'])
    @api.response(StorySchema(only=['id', 'stars']))
    def patch(self, story_id):
        """Star a story by the login user
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to star a story."
        ):
            # TODO: replace with current login user
            user = User.get(username='root')

            # Check existence of story
            story = Story.get(story_id=story_id)

            user_star = UserStarStory(user_id=user.id, story_id=story.id)
            db.session.add(user_star)

            story.stars += 1
            db.session.add(story)

            return story

    @api.login_required(oauth_scopes=['stories:write'])
    @api.response(StorySchema(only=['id', 'stars']))
    def delete(self, story_id):
        """Unstar a story by the login user
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to unstar a story."
        ):
            # TODO: replace with current login user
            user = User.get(username='root')

            # Check existence of story
            story = Story.get(story_id=story_id)

            # Unstar a story
            user_star = UserStarStory.query.filter_by(
                user_id=user.id, story_id=story.id
            ).first()

            if user_star is not None:
                db.session.delete(user_star)
                story.stars -= 1
                db.session.add(story)

            return story


@api.route('/<story_id>/comments')
@api.login_required(oauth_scopes=['stories:read'])
class StoryComments(Resource):
    @api.response(CommentSchema(many=True))
    def get(self, story_id):
        """ Get all comments of a story"""
        return Comment.get_target_comments(
            target_id=story_id,
            target_type=CommentType.STORY_COMMENT
        )

    @api.login_required(oauth_scopes=['stories:write'])
    @api.parameters(AddCommentParameters())
    @api.response(CommentSchema())
    def post(self, args, story_id):
        """ Add a new comment to a story"""
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to create a new comment for story"
        ):
            # TODO: replace with current login user
            user = User.get(username='root')

            # Check existence of story
            story = Story.get(story_id=story_id)

            # TODO: add comment flooding attack

            comment = Comment.create(
                user_id=user.id,
                target_id=story.id,
                target_type=CommentType.STORY_COMMENT,
                comment=args.get('comment')
            )

            return comment
