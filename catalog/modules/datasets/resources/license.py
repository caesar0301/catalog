import logging

from catalog.extensions import db
from catalog.extensions.flask_restplus import Namespace
from catalog.extensions.flask_restplus.parameters import PaginationParameters
from catalog.extensions.flask_restplus import Resource
from catalog.modules.datasets.models import License
from catalog.modules.datasets.parameters import AddLicenseParameters, UpdateLicenseParameters
from catalog.modules.datasets.schemas import LicenseSchema
from catalog.extensions import permissions

log = logging.getLogger(__name__)
api = Namespace('licenses', description="On licenses")


@api.route('/')
@api.login_required(oauth_scopes=['datasets:read'])
class LicenseResource(Resource):

    @api.parameters(PaginationParameters())
    @api.response(LicenseSchema(many=True))
    def get(self, args):
        """
        List of licenses.
        """
        return License.query.offset(args['offset']).limit(args['limit'])

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(AddLicenseParameters())
    @api.response(LicenseSchema())
    def post(self, args):
        """Create a new license
        """
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to create a new license."
        ):
            new_license = License.create(**args)
            db.session.add(new_license)
        return new_license


@api.route('/<license_id>')
@api.login_required(oauth_scopes=['datasets:read'])
@api.resolve_object_by_model(License, 'license', identity_arg_name='license_id')
class SingleLicense(Resource):

    @api.response(LicenseSchema())
    def get(self, license_id):
        return License.get(license_id=license_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.parameters(UpdateLicenseParameters())
    @api.response(LicenseSchema())
    def patch(self, args, license_id):
        with api.commit_or_abort(
            db.session,
            default_error_message="Failed to patch a license."
        ):
            License.query.filter_by(id=license_id).update(dict(args))
            return License.get(license_id=license_id)

    @api.login_required(oauth_scopes=['datasets:write'])
    @api.permission_required(
        permissions.OwnerRolePermission,
        kwargs_on_request=lambda kwargs: {'obj': kwargs['license']}
    )
    @api.permission_required(permissions.WriteAccessPermission())
    def delete(self, license_id):
        pass
