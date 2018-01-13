import logging

from prism.extensions import db
from prism.extensions.api import Namespace
from prism.extensions.api.parameters import PaginationParameters
from prism.extensions.flask_restplus import Resource
from prism.modules.datasets.models import Reference
from prism.modules.datasets.parameters import UpdateReferenceParameters
from prism.modules.datasets.schemas import ReferenceSchema
from prism.modules.users import permissions

log = logging.getLogger(__name__)
api = Namespace('references', description="On dataset references")


@api.route('/')
@api.login_required(oauth_scopes=['datasets:read'])
class ReferenceResource(Resource):

    @api.parameters(PaginationParameters())
    @api.response(ReferenceSchema(many=True))
    def get(self, args):
        """
        List of references.
        """
        return Reference.query.offset(args['offset']).limit(args['limit'])


@api.route('/<ref_id>')
@api.login_required(oauth_scopes=['datasets:read'])
@api.resolve_object_by_model(Reference, 'reference', identity_arg_name='ref_id')
class SingleReference(Resource):

    @api.response(ReferenceSchema())
    def get(self, ref_id):
        return Reference.get(ref_id=ref_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(UpdateReferenceParameters())
    @api.response(ReferenceSchema())
    def patch(self, args, ref_id):
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to patch a reference."
        ):
            Reference.query.filter_by(id=ref_id).update(dict(args))
            return Reference.get(ref_id=ref_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['reference']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, ref_id):
        pass
