# encoding: utf-8


def init_app(app):
    """
    Application extensions initialization.
    """
    for extension in ():
        extension.init_app(app)
