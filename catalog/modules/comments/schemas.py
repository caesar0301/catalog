from catalog.extensions.flask_restplus import ModelSchema
from catalog.modules.comments.models import Comment


class CommentSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Comment
        dump_only = (
            Comment.id.key,
            Comment.created.key,
            Comment.updated.key,
            Comment.stars.key,
            Comment.user_id.key,
            Comment.target_id.key,
            Comment.target_type.key,
        )
        fields = (
                     Comment.comment.key,
                 ) + dump_only
