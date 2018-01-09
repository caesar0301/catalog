# encoding: utf-8


def init_app(app, **kwargs):
    """
    Application modules initialization.
    """
    from importlib import import_module

    for module_name in app.config['ENABLED_MODULES']:
        import_module('.%s' % module_name, package=__name__).init_app(app, **kwargs)
