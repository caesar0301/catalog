# encoding: utf-8
from flask_marshmallow import base_fields

from catalog.extensions.flask_restplus import PostFormParameters, PatchJSONParameters
from catalog.modules.datasets import schemas
from catalog.modules.datasets.models.dataset import Dataset


class AddDatasetParameters(PostFormParameters, schemas.DatasetSchema):
    """
    New data creation parameters.
    """

    license_name = base_fields.String('license_name', required=True)
    publisher_name = base_fields.String('publisher_name')
    organization_name = base_fields.String('organization_name')

    class Meta(schemas.DatasetSchema.Meta):
        fields = schemas.DatasetSchema.Meta.fields + (
            'license_name',
            'organization_name',
            'publisher_name',
        )


class PatchDatasetParameters(PatchJSONParameters):
    """
    Updatea a dataset
    """

    PATH_CHOICES = tuple(
        '/%s' % field for field in (
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
            Dataset.license_id.key,
            Dataset.organization_id.key,
            Dataset.publisher_id.key,
        )
    )


class AddLicenseParameters(PostFormParameters, schemas.LicenseSchema):
    """
    New license creation parameters.
    """

    class Meta(schemas.LicenseSchema.Meta):
        fields = schemas.LicenseSchema.Meta.fields


class UpdateLicenseParameters(PostFormParameters, schemas.LicenseSchema):
    """
    Update a license
    """
    web = base_fields.String(required=False)
    title = base_fields.String(required=False)

    class Meta(schemas.LicenseSchema.Meta):
        fields = schemas.LicenseSchema.Meta.fields


class AddOrganizationParameters(PostFormParameters, schemas.OrganizationSchema):
    """
    New organization creation parameters.
    """

    class Meta(schemas.OrganizationSchema.Meta):
        fields = schemas.OrganizationSchema.Meta.fields


class UpdateOrganizationParameters(PostFormParameters, schemas.OrganizationSchema):
    """
    Update a organization
    """
    name = base_fields.String(required=False)

    class Meta(schemas.OrganizationSchema.Meta):
        fields = schemas.OrganizationSchema.Meta.fields


class AddPublisherParameters(PostFormParameters, schemas.PublisherSchema):
    """
    New publisher creation parameters.
    """

    class Meta(schemas.PublisherSchema.Meta):
        fields = schemas.PublisherSchema.Meta.fields


class UpdatePublisherParameters(PostFormParameters, schemas.PublisherSchema):
    """
    Update a publisher
    """
    name = base_fields.String(required=False)

    class Meta(schemas.PublisherSchema.Meta):
        fields = schemas.PublisherSchema.Meta.fields


class AddReferenceParameters(PostFormParameters, schemas.ReferenceSchema):
    """
    New reference creation parameters.
    """

    class Meta(schemas.ReferenceSchema.Meta):
        fields = schemas.ReferenceSchema.Meta.fields


class UpdateReferenceParameters(PostFormParameters, schemas.ReferenceSchema):
    """
    Update a reference
    """
    title = base_fields.String(required=False)
    reference = base_fields.String(required=False)

    class Meta(schemas.ReferenceSchema.Meta):
        fields = schemas.ReferenceSchema.Meta.fields


class AddSourceParameters(PostFormParameters, schemas.SourceSchema):
    """
    New source creation parameters.
    """

    class Meta(schemas.SourceSchema.Meta):
        fields = schemas.SourceSchema.Meta.fields


class UpdateSourceParameters(PostFormParameters, schemas.SourceSchema):
    """
    Update a source
    """
    title = base_fields.String(required=False)
    access_url = base_fields.String(required=False)
    download_url = base_fields.String(required=False)

    class Meta(schemas.SourceSchema.Meta):
        fields = schemas.SourceSchema.Meta.fields
