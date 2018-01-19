import logging

from catalog.extensions import db
from catalog.extensions import permissions
from catalog.extensions.api import Namespace
from catalog.extensions.flask_restplus.parameters import PaginationParameters
from catalog.extensions.flask_restplus import Resource
from catalog.modules.datasets.models import Publisher
from catalog.modules.datasets.parameters import AddPublisherParameters, UpdatePublisherParameters
from catalog.modules.datasets.schemas import PublisherSchema

log = logging.getLogger(__name__)
api = Namespace('publishers', description="On publishers")


@api.route('/')
@api.login_required(oauth_scopes=['datasets:read'])
class PublisherResource(Resource):
    @api.parameters(PaginationParameters())
    @api.response(PublisherSchema(many=True))
    def get(self, args):
        """
        List of publishers.
        """
        return Publisher.query.offset(args['offset']).limit(args['limit'])

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddPublisherParameters())
    @api.response(PublisherSchema())
    def post(self, args):
        """Create a new publisher
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to create a new publisher."
        ):
            new_publisher = Publisher.create(**args)
            db.session.add(new_publisher)
        return new_publisher


@api.route('/<publisher_id>')
@api.login_required(oauth_scopes=['datasets:read'])
@api.resolve_object_by_model(Publisher, 'publisher', identity_arg_name='publisher_id')
class SinglePublisher(Resource):
    @api.response(PublisherSchema())
    def get(self, publisher_id):
        return Publisher.get(publisher_id=publisher_id)

    @api.parameters(UpdatePublisherParameters())
    @api.response(PublisherSchema())
    def patch(self, args, publisher_id):
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to patch a publisher."
        ):
            Publisher.query.filter_by(id=publisher_id).update(dict(args))
            return Publisher.get(publisher_id=publisher_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['publisher']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, publisher_id):
        pass
