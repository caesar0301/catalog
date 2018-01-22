# encoding: utf-8


def init_app(app, **kwargs):
    from . import views

    app.register_blueprint(views.landing_blueprint)
