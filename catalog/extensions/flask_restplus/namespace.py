# encoding: utf-8
"""
Extended Api Namespace implementation with an application-specific helpers
--------------------------------------------------------------------------
"""
import logging
from contextlib import contextmanager
from functools import wraps
from http import HTTPStatus

import flask
import flask_marshmallow
import sqlalchemy
from flask_restplus import Namespace as OriginalNamespace
from flask_restplus.utils import merge
from webargs.flaskparser import FlaskParser
from werkzeug import exceptions as http_exceptions

from catalog.extensions.flask_restplus.errors import abort
from .model import Model
from .schema import DefaultHTTPErrorSchema

logger = logging.getLogger(__name__)


class CustomWebargsParser(FlaskParser):
    """
    This custom Webargs Parser aims to overload :meth:``handle_error`` in order
    to call our custom :func:``abort`` function.

    See the following issue and the reated PR for more details:
    https://github.com/sloria/webargs/issues/122
    """

    def handle_error(self, error):
        """
        Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = getattr(error, 'status_code', self.DEFAULT_VALIDATION_STATUS)
        abort(status_code, messages=error.messages)


class Namespace(OriginalNamespace):
    """
    Having app-specific handlers here.
    """

    WEBARGS_PARSER = CustomWebargsParser()

    def _handle_api_doc(self, cls, doc):
        if doc is False:
            cls.__apidoc__ = False
            return
        cls.__apidoc__ = merge(getattr(cls, '__apidoc__', {}), doc)

    def resolve_object(self, object_arg_name, resolver):
        """
        A helper decorator to resolve object instance from arguments (e.g. identity).

        Example:
        >>> @namespace.route('/<int:user_id>')
        ... class MyResource(Resource):
        ...    @namespace.resolve_object(
        ...        object_arg_name='user',
        ...        resolver=lambda kwargs: User.query.get_or_404(kwargs.pop('user_id'))
        ...    )
        ...    def get(self, user):
        ...        # user is a User instance here
        """

        def decorator(func_or_class):
            if isinstance(func_or_class, type):
                # Handle Resource classes decoration
                func_or_class._apply_decorator_to_methods(decorator)
                return func_or_class

            @wraps(func_or_class)
            def wrapper(*args, **kwargs):
                kwargs[object_arg_name] = resolver(kwargs)
                return func_or_class(*args, **kwargs)

            return wrapper

        return decorator

    def model(self, name=None, model=None, mask=None, **kwargs):
        """
        Model registration decorator.
        """
        if isinstance(model, (flask_marshmallow.Schema, flask_marshmallow.base_fields.FieldABC)):
            if not name:
                name = model.__class__.__name__
                if name.endswith('Schema'):
                    name = name[:-len('Schema')]
            api_model = Model(name, model, mask=mask)
            api_model.__apidoc__ = kwargs
            return self.add_model(name, api_model)
        return super(Namespace, self).model(name, model, **kwargs)

    def parameters(self, parameters, locations=None):
        """
        Endpoint parameters registration decorator.
        """

        def decorator(func):
            if locations is None and parameters.many:
                _locations = ('json',)
            else:
                _locations = locations
            if _locations is not None:
                parameters.context['in'] = _locations

            return self.doc(params=parameters)(
                self.response(code=HTTPStatus.UNPROCESSABLE_ENTITY)(
                    self.WEBARGS_PARSER.use_args(parameters, locations=_locations)(
                        func
                    )
                )
            )

        return decorator

    def response(self, model=None, code=HTTPStatus.OK, description=None, **kwargs):
        """
        Endpoint response OpenAPI documentation decorator.

        It automatically documents HTTPError%(code)d responses with relevant
        schemas.

        Arguments:
            model (flask_marshmallow.Schema) - it can be a class or an instance
                of the class, which will be used for OpenAPI documentation
                purposes. It can be omitted if ``code`` argument is set to an
                error HTTP status code.
            code (int) - HTTP status code which is documented.
            description (str)

        Example:
        >>> @namespace.response(BaseTeamSchema(many=True))
        ... @namespace.response(code=HTTPStatus.FORBIDDEN)
        ... def get_teams():
        ...     if not user.is_admin:
        ...         abort(HTTPStatus.FORBIDDEN)
        ...     return Team.query.all()
        """
        code = HTTPStatus(code)
        if code is HTTPStatus.NO_CONTENT:
            assert model is None
        if model is None and code not in {HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT}:
            if code.value not in http_exceptions.default_exceptions:
                raise ValueError("`model` parameter is required for code %d" % code)
            model = self.model(
                name='HTTPError%d' % code,
                model=DefaultHTTPErrorSchema(http_code=code)
            )
        if description is None:
            description = code.description

        def response_serializer_decorator(func):
            """
            This decorator handles responses to serialize the returned value
            with a given model.
            """

            def dump_wrapper(*args, **kwargs):
                response = func(*args, **kwargs)

                if response is None:
                    if model is not None:
                        raise ValueError("Response cannot not be None with HTTP status %d" % code)
                    return flask.Response(status=code)
                elif isinstance(response, flask.Response) or model is None:
                    return response
                elif isinstance(response, tuple):
                    response, _code = response
                else:
                    _code = code

                if HTTPStatus(_code) is code:
                    response = model.dump(response).data
                return response, _code

            return dump_wrapper

        def decorator(func_or_class):
            if code.value in http_exceptions.default_exceptions:
                # If the code is handled by raising an exception, it will
                # produce a response later, so we don't need to apply a useless
                # wrapper.
                decorated_func_or_class = func_or_class
            elif isinstance(func_or_class, type):
                # Handle Resource classes decoration
                func_or_class._apply_decorator_to_methods(response_serializer_decorator)
                decorated_func_or_class = func_or_class
            else:
                decorated_func_or_class = wraps(func_or_class)(
                    response_serializer_decorator(func_or_class)
                )

            if model is None:
                api_model = None
            else:
                if isinstance(model, Model):
                    api_model = model
                else:
                    api_model = self.model(model=model)
                if getattr(model, 'many', False):
                    api_model = [api_model]

            doc_decorator = self.doc(
                responses={
                    code.value: (description, api_model)
                }
            )
            return doc_decorator(decorated_func_or_class)

        return decorator

    def preflight_options_handler(self, func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if 'Access-Control-Request-Method' in flask.request.headers:
                response = flask.Response(status=HTTPStatus.OK)
                response.headers['Access-Control-Allow-Methods'] = ", ".join(self.methods)
                return response
            return func(self, *args, **kwargs)

        return wrapper

    def route(self, *args, **kwargs):
        base_wrapper = super(Namespace, self).route(*args, **kwargs)

        def wrapper(cls):
            if 'OPTIONS' in cls.methods:
                cls.options = self.preflight_options_handler(
                    self.response(code=HTTPStatus.NO_CONTENT)(cls.options)
                )
            return base_wrapper(cls)

        return wrapper

    def resolve_object_by_model(self, model, object_arg_name, identity_arg_name=None):
        """
        A helper decorator to resolve DB record instance by id.

        Arguments:
            model (type) - a Flask-SQLAlchemy model class with
                ``query.get_or_404`` method
            object_arg_name (str) - argument name for a resolved object
            identity_arg_name (str) - argument name holding an object identity,
                by default it will be auto-generated as
                ``%(object_arg_name)s_id``.

        Example:
        >>> @namespace.resolve_object_by_model(User, 'user')
        ... def get_user_by_id(user):
        ...     return user
        >>> get_user_by_id(user_id=3)
        <User(id=3, ...)>
        """
        if identity_arg_name is None:
            identity_arg_name = '%s_id' % object_arg_name
        return self.resolve_object(
            object_arg_name,
            resolver=lambda kwargs: model.query.get_or_404(kwargs.pop(identity_arg_name))
        )

    def login_required(self, oauth_scopes):
        """
        A decorator which restricts access for authorized users only.

        This decorator automatically applies the following features:

        * ``OAuth2.require_oauth`` decorator requires authentication;
        * ``permissions.ActiveUserRolePermission`` decorator ensures
          minimal authorization level;
        * All of the above requirements are put into OpenAPI Specification with
          relevant options and in a text description.

        Arguments:
            oauth_scopes (list) - a list of required OAuth2 Scopes (strings)

        Example:
        >>> @namespace.login_required(oauth_scopes=['users:read'])
        ... class Users(Resource):
        ...     def get(self):
        ...         return []
        ...
        ...     @namespace.login_required(oauth_scopes=['users:write'])
        ...     def post(self):
        ...         return User()
        """

        def decorator(func_or_class):
            """
            A helper wrapper.
            """
            if isinstance(func_or_class, type):
                # Handle Resource classes decoration
                func_or_class._apply_decorator_to_methods(decorator)
                return func_or_class
            else:
                func = func_or_class

            # Avoid circular dependency
            from catalog.extensions import oauth2, permissions

            # Automatically apply `permissions.ActiveUserRolePermisson`
            # guard if none is yet applied.
            if getattr(func, '_role_permission_applied', False):
                protected_func = func
            else:
                protected_func = self.permission_required(
                    permissions.ActiveUserRolePermission()
                )(func)

            # Ignore the current OAuth2 scopes if another @login_required
            # decorator was applied and just copy the already applied scopes.
            if hasattr(protected_func, '__apidoc__') \
                    and 'security' in protected_func.__apidoc__ \
                    and '__oauth__' in protected_func.__apidoc__['security']:
                _oauth_scopes = protected_func.__apidoc__['security']['__oauth__']['scopes']
            else:
                _oauth_scopes = oauth_scopes

            oauth_protection_decorator = oauth2.require_oauth(*_oauth_scopes)
            self._register_access_restriction_decorator(protected_func, oauth_protection_decorator)
            oauth_protected_func = oauth_protection_decorator(protected_func)

            return self.doc(
                security={
                    # This is a temporary configuration which is overridden in
                    # `Api.add_namespace`.
                    '__oauth__': {
                        'type': 'oauth',
                        'scopes': _oauth_scopes,
                    }
                }
            )(
                self.response(
                    code=HTTPStatus.UNAUTHORIZED.value,
                    description=(
                        "Authentication is required"
                        if not oauth_scopes else
                        "Authentication with %s OAuth scope(s) is required" % (
                            ', '.join(oauth_scopes)
                        )
                    ),
                )(oauth_protected_func)
            )

        return decorator

    def permission_required(self, permission, kwargs_on_request=None):
        """
        A decorator which restricts access for users with a specific
        permissions only.

        This decorator puts together permissions restriction code with OpenAPI
        Specification documentation.

        Arguments:
            permission (Permission) - it can be a class or an instance of
                :class:``Permission``, which will be applied to a decorated
                function, and docstrings of which will be used in OpenAPI
                Specification.
            kwargs_on_request (func) - a function which should accept only one
                ``dict`` argument (all kwargs passed to the function), and
                must return a ``dict`` of arguments which will be passed to
                the ``permission`` object.

        Example:
        >>> @namespace.permission_required(
        ...     OwnerRolePermission,
        ...     kwargs_on_request=lambda kwargs: {'obj': kwargs['team']}
        ... )
        ... def get_team(team):
        ...     # This line will be reached only if OwnerRolePermission check
        ...     # is passed!
        ...     return team
        """

        def decorator(func):
            """
            A helper wrapper.
            """
            # Avoid circular dependency
            from catalog.extensions import permissions

            if getattr(permission, '_partial', False):
                # We don't apply partial permissions, we only use them for
                # documentation purposes.
                protected_func = func
            else:
                if not kwargs_on_request:
                    _permission_decorator = permission
                else:
                    def _permission_decorator(func):
                        @wraps(func)
                        def wrapper(*args, **kwargs):
                            with permission(**kwargs_on_request(kwargs)):
                                return func(*args, **kwargs)

                        return wrapper

                protected_func = _permission_decorator(func)
                self._register_access_restriction_decorator(protected_func, _permission_decorator)

            # Apply `_role_permission_applied` marker for Role Permissions,
            # so don't apply unnecessary permissions in `login_required`
            # decorator.
            #
            # TODO: Change this behaviour when implement advanced OPTIONS
            # method support
            if (isinstance(permission, permissions.RolePermission)
                or (isinstance(permission, type)
                    and issubclass(permission, permissions.RolePermission))):
                protected_func._role_permission_applied = True

            permission_description = permission.__doc__.strip()
            return self.doc(
                description="**PERMISSIONS: %s**\n\n" % permission_description
            )(
                self.response(
                    code=HTTPStatus.FORBIDDEN.value,
                    description=permission_description,
                )(protected_func)
            )

        return decorator

    def _register_access_restriction_decorator(self, func, decorator_to_register):
        """
        Helper function to register decorator to function to perform checks
        in options method
        """
        if not hasattr(func, '_access_restriction_decorators'):
            func._access_restriction_decorators = []
        func._access_restriction_decorators.append(decorator_to_register)

    @contextmanager
    def commit_or_abort(self, session, default_error_message="The operation failed to complete"):
        """
        Context manager to simplify a workflow in resources

        Args:
            session: db.session instance
            default_error_message: Custom error message

        Exampple:
        >>> with api.commit_or_abort(db.session):
        ...     user = User(**args)
        ...     db.session.add(user)
        ...     return user
        """
        default_error_message = default_error_message.strip('.:')
        try:
            with session.begin():
                yield
        except ValueError as exception:
            logger.error("Value error to commit data: {}".format(str(exception)))
            abort(code=HTTPStatus.CONFLICT, message=str(exception))
        except sqlalchemy.exc.IntegrityError as e:
            logger.error("Database integrity error: {}".format(str(e)))
            abort(
                code=HTTPStatus.CONFLICT,
                message="{}: {}".format(default_error_message, str(e))
            )
        except Exception as e:
            logger.error("Failed to commit data: {}".format(str(e)))
            if hasattr(e, 'code'):
                code = e.code
            else:
                code = HTTPStatus.BAD_REQUEST
            abort(
                code=code,
                message="{}: {}".format(default_error_message, str(e))
            )
