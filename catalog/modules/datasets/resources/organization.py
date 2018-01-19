import logging

from catalog.extensions import db
from catalog.extensions import permissions
from catalog.extensions.flask_restplus import Namespace
from catalog.extensions.flask_restplus.parameters import PaginationParameters
from catalog.extensions.flask_restplus import Resource
from catalog.modules.datasets.models import Organization
from catalog.modules.datasets.parameters import AddOrganizationParameters, UpdateOrganizationParameters
from catalog.modules.datasets.schemas import OrganizationSchema

log = logging.getLogger(__name__)
api = Namespace('organizations', description="On organizations")


@api.route('/')
@api.login_required(oauth_scopes=['datasets:read'])
class OrganizationResource(Resource):
    @api.parameters(PaginationParameters())
    @api.response(OrganizationSchema(many=True))
    def get(self, args):
        """
        List of organizations.
        """
        return Organization.query.offset(args['offset']).limit(args['limit'])

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddOrganizationParameters())
    @api.response(OrganizationSchema())
    def post(self, args):
        """Create a new organization
        """
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to create a new organization."
        ):
            new_org = Organization.create(**args)
            db.session.add(new_org)
        return new_org


@api.route('/<org_id>')
@api.login_required(oauth_scopes=['datasets:read'])
@api.resolve_object_by_model(Organization, 'organization', identity_arg_name='org_id')
class SingleOrganization(Resource):
    @api.response(OrganizationSchema())
    def get(self, org_id):
        return Organization.get(org_id=org_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(UpdateOrganizationParameters())
    @api.response(OrganizationSchema())
    def patch(self, args, org_id):
        with api.commit_or_abort(
                db.session,
                default_error_message="Failed to patch a organization."
        ):
            Organization.query.filter_by(id=org_id).update(dict(args))
            return Organization.get(org_id=org_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['organization']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, org_id):
        pass
