# encoding: utf-8

from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import PostFormParameters
from catalog.modules.stories import schemas


class AddStoryParameters(PostFormParameters, schemas.StorySchema):
    """
    New story creation parameters.
    """

    class Meta(schemas.StorySchema.Meta):
        fields = schemas.StorySchema.Meta.fields


class UpdateStoryParameters(PostFormParameters, schemas.StorySchema):
    """
    Story updating parameters.
    """
    title = base_fields.String(required=False)
    web = base_fields.String(required=False)

    class Meta(schemas.StorySchema.Meta):
        fields = schemas.StorySchema.Meta.fields
