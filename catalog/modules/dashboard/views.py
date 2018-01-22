# coding: utf-8
from flask import Blueprint, request, render_template

dashboard_blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_blueprint.route('/', methods=['GET', 'POST'])
def dashboard(*args, **kwargs):
    if request.method == 'GET':
        return render_template('dashboard.html', **kwargs)

    return "Unsupported method: {}".format(request.method)
