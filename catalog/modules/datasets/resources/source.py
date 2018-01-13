import logging

from prism.extensions import db
from prism.extensions.api import Namespace
from prism.extensions.api.parameters import PaginationParameters
from prism.extensions.flask_restplus import Resource
from prism.modules.datasets.models import Source
from prism.modules.datasets.parameters import UpdateSourceParameters
from prism.modules.datasets.schemas import SourceSchema
from prism.modules.users import permissions

log = logging.getLogger(__name__)
api = Namespace('sources', description="On dataset sources")


@api.route('/')
@api.login_required(oauth_scopes=['datasets:read'])
class SourceResource(Resource):

    @api.parameters(PaginationParameters())
    @api.response(SourceSchema(many=True))
    def get(self, args):
        """
        List of sources.
        """
        return Source.query.offset(args['offset']).limit(args['limit'])


@api.route('/<source_id>')
@api.login_required(oauth_scopes=['datasets:read'])
@api.resolve_object_by_model(Source, 'source', identity_arg_name='source_id')
class SingleSource(Resource):

    @api.response(SourceSchema())
    def get(self, source_id):
        return Source.get(source_id=source_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(UpdateSourceParameters())
    @api.response(SourceSchema())
    def patch(self, args, source_id):
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to patch a source."
        ):
            Source.query.filter_by(id=source_id).update(dict(args))
            return Source.get(source_id=source_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['source']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, source_id):
        pass
