from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import parameters
from catalog.modules.comments import schemas, models


class AddCommentParameters(parameters.PostFormParameters, schemas.CommentSchema):
    target_id = base_fields.String(required=False)
    target_type = base_fields.String(required=False)
    user_id = base_fields.String(required=False)

    class Meta(schemas.CommentSchema.Meta):
        fields = schemas.CommentSchema.Meta.fields


class UpdateCommentParameters(parameters.PatchJSONParameters):
    OPERATION_CHOICES = (
        parameters.PatchJSONParameters.OP_REPLACE,
    )

    PATH_CHOICES = tuple(
        '/%s' % field for field in (
            models.Comment.comment.key,
        )
    )
