# encoding: utf-8


def init_app(app, **kwargs):
    """
    Init auth module.
    """
    # Touch underlying modules
    from . import views

    # Mount authentication routes
    app.register_blueprint(views.dashboard_blueprint)
