# encoding: utf-8
"""
Dataset schemas
------------
"""

from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import ModelSchema
from catalog.modules.datasets.models import Dataset, Organization, Publisher, Reference, Source, License


class DatasetSchema(ModelSchema):
    """
    Base dataset schema exposes only the most general fields.
    """

    license = base_fields.Nested('LicenseSchema')
    organization = base_fields.Nested('OrganizationSchema')
    publisher = base_fields.Nested('PublisherSchema')
    sources = base_fields.Nested('SourceSchema', many=True)
    references = base_fields.Nested('ReferenceSchema', many=True)
    contributor = base_fields.Nested('UserSchema')
    story_count = base_fields.Method(serialize='count_stories')

    class Meta:
        model = Dataset
        fields = (
            # Inner dimensions
            Dataset.id.key,
            Dataset.created.key,
            Dataset.updated.key,
            Dataset.stars.key,
            # Basic dimensions
            Dataset.name.key,
            Dataset.title.key,
            Dataset.description.key,
            Dataset.homepage.key,
            Dataset.version.key,
            Dataset.category.key,
            Dataset.issued_time.key,
            Dataset.keywords.key,
            Dataset.image.key,
            Dataset.temporal.key,
            Dataset.spatial.key,
            Dataset.access_level.key,
            Dataset.copyrights.key,
            Dataset.accrual_periodicity.key,
            Dataset.specification.key,
            Dataset.data_quality.key,
            Dataset.data_dictionary.key,
            Dataset.language.key,
            # Detailed dimensions
            'contributor',  # Local user
            'license',
            'organization',
            'publisher',
            'sources',
            'references',
            'story_count'
        )
        dump_only = (
            Dataset.id.key,
            Dataset.created.key,
            Dataset.updated.key,
            Dataset.stars.key,
            'contributor',
            'license',
            'organization',
            'publisher',
            'sources',
            'references',
            'story_count'
        )

    def count_stories(self, dataset):
        assert isinstance(dataset, Dataset)
        return dataset.associated_stories_num()


class LicenseSchema(ModelSchema):
    class Meta:
        model = License
        fields = (
            License.id.key,
            License.title.key,
            License.web.key,
            License.type.key,
            License.created.key,
            License.updated.key,
        )
        dump_only = (
            License.id.key,
            License.created.key,
            License.updated.key,
        )


class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = (
            Organization.id.key,
            Organization.name.key,
            Organization.email.key,
            Organization.web.key,
            Organization.country.key,
            Organization.created.key,
            Organization.updated.key,
        )
        dump_only = (
            Organization.id.key,
            Organization.created.key,
            Organization.updated.key
        )


class PublisherSchema(ModelSchema):
    class Meta:
        model = Publisher
        fields = (
            Publisher.id.key,
            Publisher.name.key,
            Publisher.department.key,
            Publisher.web.key,
            Publisher.email.key,
            Publisher.role.key,
            Publisher.created.key,
            Publisher.updated.key,
            Publisher.organization_id.key
        )
        dump_only = (
            Publisher.id.key,
            Publisher.created.key,
            Publisher.updated.key,
        )


class ReferenceSchema(ModelSchema):
    class Meta:
        model = Reference
        fields = (
            Reference.id.key,
            Reference.dataset_id.key,
            Reference.title.key,
            Reference.reference.key,
            Reference.snapshot.key,
            Reference.created.key,
            Reference.updated.key,
        )
        dump_only = (
            Reference.id.key,
            Reference.created.key,
            Reference.updated.key,
        )


class SourceSchema(ModelSchema):
    class Meta:
        model = Source
        fields = (
            Source.id.key,
            Source.dataset_id.key,
            Source.title.key,
            Source.access_url.key,
            Source.download_url.key,
            Source.email.key,
            Source.description.key,
            Source.format.key,
            Source.media_type.key,
            Source.schema.key,
            Source.created.key,
            Source.updated.key,
            Source.snapshot.key,
        )
        dump_only = (
            Source.id.key,
            Source.snapshot.key,
            Source.created.key,
            Source.updated.key,
        )
