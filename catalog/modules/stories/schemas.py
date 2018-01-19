# encoding: utf-8
"""
Story schemas
------------
"""
import json
import logging
from http import HTTPStatus

from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import ModelSchema
from catalog.extensions.flask_restplus.errors import abort
from catalog.modules.stories.models import Story, StoryAcademic, StoryNews, StoryType

logger = logging.getLogger(__name__)


class StoryAcademicSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = StoryAcademic
        fields = (
            StoryAcademic.story_id.key,
            StoryAcademic.paper_name.key,
            StoryAcademic.paper_link.key,
            StoryAcademic.paper_authors.key,
            StoryAcademic.paper_org.key,
            StoryAcademic.code_repo.key,
        )


class StoryNewsSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = StoryNews
        ordered = True
        fields = (
            StoryNews.story_id.key,
            StoryNews.title.key,
            StoryNews.people.key,
            StoryNews.date.key,
            StoryNews.location.key,
            StoryNews.country.key,
        )


# Mapping between story types and model fields
story_details_fields = {
    StoryType.ACADEMIC: 'academic_story',
    StoryType.NEWS: 'news_story'
}

# Mapping between story types and details schema
story_details_schema = {
    StoryType.ACADEMIC: StoryAcademicSchema(),
    StoryType.NEWS: StoryNewsSchema(),
}


class StorySchema(ModelSchema):
    contributor = base_fields.Nested('UserSchema')
    details = base_fields.Method(serialize='dump_story_details',
                                 deserialize='load_story_details')

    class Meta(ModelSchema.Meta):
        model = Story
        dump_only = (
            Story.id.key,
            Story.created.key,
            Story.updated.key,
            'contributor',
        )
        fields = (
                     Story.id.key,
                     Story.title.key,
                     Story.web.key,
                     Story.description.key,
                     Story.category.key,
                     Story.type.key,
                     Story.stars.key,
                     Story.keywords.key,
                     Story.issued_time.key,
                     'details',
                 ) + dump_only

    def load_story_details(self, value):
        """
        Load details field into corresponding story schema
        """
        if isinstance(value, str):
            value = json.loads(value)
        story_type = int(value.get('type', StoryType.INVALID))
        if story_type != StoryType.INVALID:
            schema = story_details_schema.get(story_type)
            if schema is not None:
                obj = schema.load(value)
                if obj.errors:
                    abort(code=HTTPStatus.BAD_REQUEST, message=str(obj.errors))
                return obj.data
            return None

    def dump_story_details(self, story_obj):
        """
        Format story details.
        :param story_obj: an instance of Story
        :return: detailed Schema or empty
        """
        assert isinstance(story_obj, Story)
        res = dict()
        details_field = story_details_fields.get(story_obj.type)

        # TODO: raise meaingful exception

        if details_field is not None:
            details = getattr(story_obj, details_field)
            schema = story_details_schema.get(story_obj.type)
            if schema is not None:
                res = schema.dump(details)
                if res.errors:
                    abort(code=HTTPStatus.BAD_REQUEST, message=str(res.errors))
                return res.data
        return res


class StoryStatSchema(ModelSchema):
    associated_datasets = base_fields.Method(serialize='count_datasets')

    class Meta(ModelSchema.Meta):
        model = Story
        fields = (
            'id',
            'associated_datasets'
        )

    def count_datasets(self, story_obj):
        return story_obj.associated_datasets_num()
