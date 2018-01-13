# encoding: utf-8
"""
RESTful API Dataset resources
--------------------------
"""
import logging
from http import HTTPStatus
from flask_login import current_user

from prism.exception import PrismException
from prism.extensions import db
from prism.extensions.api import Namespace
from prism.extensions.api.parameters import PaginationParameters
from prism.extensions.flask_restplus import Resource
from prism.modules.comments.models import Comment, CommentType
from prism.modules.comments.parameters import AddCommentParameters
from prism.modules.comments.schemas import CommentSchema
from prism.modules.datasets.models import Dataset, License, Organization, Publisher, Reference, Source
from prism.modules.datasets.parameters import AddDatasetParameters, PatchDatasetParameters
from prism.modules.datasets.parameters import AddReferenceParameters, AddSourceParameters
from prism.modules.datasets.schemas import DatasetSchema, ReferenceSchema, SourceSchema
from prism.modules.stories.models import Story, StoryDatasetAssociation
from prism.modules.stories.parameters import AddStoryParameters
from prism.modules.stories.schemas import StorySchema
from prism.modules.users.models import UserStarDataset
from prism.modules.users import permissions
from prism.exception import ObjectDoesNotExist

log = logging.getLogger(__name__)
api = Namespace('datasets', description="On datasets")


@api.route("/")
@api.login_required(oauth_scopes=['datasets:read'])
class DatasetResource(Resource):
    """
    Manipulations with datasets
    """

    @api.parameters(PaginationParameters())
    @api.response(DatasetSchema(many=True))
    def get(self, args):
        """
        List of all datasets

        :param args: query parameters
        :return: a list of datasets starting from ``offset`` limited by
        ``limit`` parameter.
        """
        return Dataset.query.filter_by(deleted=False)\
            .offset(args['offset'])\
            .limit(args['limit'])

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddDatasetParameters())
    @api.response(DatasetSchema())
    @api.response(code=HTTPStatus.CONFLICT)
    def post(self, args):
        """Create a new dataset
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to create a new dataset."
        ):
            contributor = current_user
            args['contributor_id'] = contributor.id

            if 'license_name' in args:
                license_name = args.pop('license_name')
                try:
                    license = License.get(license_name=license_name)
                except ObjectDoesNotExist:
                    log.warning('License "{}" not found, and created automatically.'.format(license_name))
                    license = License.create(title=license_name)
                args['license_id'] = license.id

            if 'organization_name' in args:
                organization_name = args.pop('organization_name')
                try:
                    organization = Organization.get(org_name=organization_name)
                except ObjectDoesNotExist:
                    log.warning('Organization "{}" not found, and created automatically.'.format(organization_name))
                    organization = Organization.create(name=organization_name)
                args['organization_id'] = organization.id

            if 'publisher_name' in args:
                publisher_name = args.pop('publisher_name')
                try:
                    publisher = Publisher.get(publisher_name=publisher_name)
                except ObjectDoesNotExist:
                    log.warning('Publisher "{}" not found, and created automatically.'.format(publisher_name))
                    publisher = Publisher.create(name=publisher_name)
                args['publisher_id'] = publisher.id

            return Dataset.create(**args)


@api.route("/<id>")
@api.resolve_object_by_model(Dataset, 'dataset', identity_arg_name='id')
@api.login_required(oauth_scopes=['datasets:read'])
class SingleDatasetResource(Resource):
    """
    Manipulations with a specific dataset.
    """

    @api.response(DatasetSchema())
    def get(self, dataset):
        """ Get a specific dataset
        """
        return dataset

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['dataset']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.parameters(PatchDatasetParameters())
    @api.response(DatasetSchema())
    def patch(self, args, dataset):
        """ Update a dataset
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to patch a dataset."
        ):
            PatchDatasetParameters.perform_patch(args, dataset)
            db.session.merge(dataset)
        return dataset

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['dataset']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(code=HTTPStatus.CONFLICT)
    def delete(self, dataset):
        """ Delete a specific dataset (TODO)"""
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to delete a dataset."
        ):
            Dataset.delete(dataset=dataset)


@api.route("/<dataset_id>/references")
@api.login_required(oauth_scopes=['datasets:read'])
class DatasetReferences(Resource):
    """
    Manipulations with dataset references.
    """

    @api.response(ReferenceSchema(many=True))
    def get(self, dataset_id):
        """ Get all references of a dataset"""
        return Reference.get(dataset_id=dataset_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddReferenceParameters(exclude=['dataset_id']))
    @api.response(ReferenceSchema())
    def post(self, args, dataset_id):
        """Create a new reference for a dataset
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to create a new reference."
        ):
            args['dataset_id'] = dataset_id
            new_ref = Reference.create(**args)
            db.session.add(new_ref)
            return new_ref


@api.route("/<dataset_id>/sources")
@api.login_required(oauth_scopes=['datasets:read'])
class DatasetSources(Resource):
    """
    Manipulations with dataset sources.
    """

    @api.response(SourceSchema(many=True))
    def get(self, dataset_id):
        """ Get all sources of a dataset"""
        return Source.get(dataset_id=dataset_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddSourceParameters(exclude=['dataset_id']))
    @api.response(SourceSchema())
    def post(self, args, dataset_id):
        """Create a new source for a dataset
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to create a new data source."
        ):
            args['dataset_id'] = dataset_id
            new_ref = Source.create(**args)
            db.session.add(new_ref)
            return new_ref


@api.route('/<dataset_id>/stars')
@api.login_required(oauth_scopes=['datasets:read'])
class StarDatasetAction(Resource):
    """
    Manipulations with a dataset stars.
    """

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.response(DatasetSchema(only=['id', 'stars']))
    def patch(self, dataset_id):
        """Star a dataset by the login user
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to star a dataset."
        ):
            user = current_user

            # Check existence of dataset
            dataset = Dataset.get(id=dataset_id)

            user_star = UserStarDataset(user_id=user.id, dataset_id=dataset.id)
            db.session.add(user_star)

            dataset.stars += 1
            db.session.add(dataset)

            return dataset

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.response(DatasetSchema(only=['id', 'stars']))
    def delete(self, dataset_id):
        """Unstar a dataset by the login user
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to unstar a dataset."
        ):
            user = current_user

            # Check existence of dataset
            dataset = Dataset.get(id=dataset_id)
            user_star = UserStarDataset.query.filter_by(
                user_id=user.id, dataset_id=dataset.id
            ).first()

            if user_star is not None:
                db.session.delete(user_star)
                dataset.stars -= 1
                db.session.add(dataset)

            return dataset


@api.route('/<dataset_id>/comments')
@api.login_required(oauth_scopes=['datasets:read'])
class DatasetComments(Resource):
    """
    Manipulations with a dataset comments.
    """

    @api.response(CommentSchema(many=True))
    def get(self, dataset_id):
        """ Get all comments of a dataset"""
        return Comment.get_target_comments(
            target_id=dataset_id,
            target_type=CommentType.DATASET_COMMENT
        )

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddCommentParameters())
    @api.response(CommentSchema())
    def post(self, args, dataset_id):
        """ Add a new comment for a dataset"""
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to create a new comment for dataset"
        ):
            user = current_user

            # Check existence of dataset
            dataset = Dataset.get(id=dataset_id)

            # TODO: add comment flooding attack

            comment = Comment.create(
                user_id=user.id,
                target_id=dataset.id,
                target_type=CommentType.DATASET_COMMENT,
                comment=args.get('comment')
            )

            return comment


##########################
# Stories about datasets
##########################

@api.route("/<dataset_id>/stories")
@api.login_required(oauth_scopes=['stories:read'])
class DatasetStories(Resource):
    """
    Manipulations with a dataset's stories.
    """

    @api.response(StorySchema(many=True))
    def get(self, dataset_id):
        """ Get all associated stories of a dataset"""
        associations = Dataset.get(id=dataset_id).stories_association
        return [i.story for i in associations]

    @api.login_required(oauth_scopes=['stories:write'])
    @api.parameters(AddStoryParameters())
    @api.response(StorySchema())
    def post(self, args, dataset_id):
        """ Create a new story for a dataset"""
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to create a new data story."
        ):
            contributor = current_user
            args['contributor_id'] = contributor.id

            # Check existing dataset
            dataset = Dataset.get(id=dataset_id)

            # Detail object resolved by parameter handler
            details_obj = args.pop('details', None)
            new_story = Story.create(details_obj, **args)

            # Update dataset-story link
            association = StoryDatasetAssociation(linker_id=contributor.id)
            association.dataset = dataset
            new_story.datasets_association.append(association)
            db.session.add(new_story)

            return new_story


@api.route('/<dataset_id>/stories/<story_id>/links')
@api.login_required(oauth_scopes=['datasets:read'])
class DatasetStoryLinkAction(Resource):
    """
    Manipulations with a dataset-story link.
    """

    @api.login_required(oauth_scopes=['stories:write'])
    @api.response(DatasetSchema(only=['id', 'story_count']))
    def patch(self, story_id, dataset_id):
        """Create a new link between a story and a dataset
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to link a story and dataset."
        ):
            user = current_user

            # Check existence of dataset and story

            dataset = Dataset.get(id=dataset_id)
            story = Story.get(story_id=story_id)

            sd = StoryDatasetAssociation(
                story_id=story.id, dataset_id=dataset.id,
                linker_id=user.id
            )
            db.session.add(sd)

            return dataset

    @api.login_required(oauth_scopes=['stories:write'])
    @api.permission_required(permissions.WriteAccessPermission())
    @api.response(DatasetSchema(only=['id', 'story_count']))
    def delete(self, story_id, dataset_id):
        """Remove the link between a dataset and a story
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to unlink a story and dataset."
        ):
            user = current_user

            # Check existence of dataset and story
            dataset = Dataset.get(id=dataset_id)
            story = Story.get(story_id=story_id)

            # TODO: unauthorized to unlink others' post.
            sd = StoryDatasetAssociation.query.filter_by(
                story_id=story.id, dataset_id=dataset.id,
                linker_id=user.id
            ).first()

            if sd is not None:
                db.session.delete(sd)
            else:
                raise PrismException('Unlinked already')

            return dataset
