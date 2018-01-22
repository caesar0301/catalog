# coding: utf-8
from flask import Blueprint, render_template

landing_blueprint = Blueprint('landing', __name__, url_prefix='/')


@landing_blueprint.route('/', methods=['GET'])
def landing_page(*args, **kwargs):
    return render_template('index.html', **kwargs)
