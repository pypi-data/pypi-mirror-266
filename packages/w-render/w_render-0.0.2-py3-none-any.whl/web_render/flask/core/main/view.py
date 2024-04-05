"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from flask import Blueprint, jsonify, render_template
from web_render.flask.core.service.interface import MessageProtocol


main_bp = Blueprint('main', __name__, template_folder="templates")
result01 = MessageProtocol(message="Successful", payload=[1,2,3], status_code=200, action="")
result02 = MessageProtocol(message="Error", payload=None, status_code=403, action="")


@main_bp.route("/data")
def data():
    return  jsonify(result01.to_dict()), result01.status_code


@main_bp.route("/error")
def err_data():
    return jsonify(result02.to_dict()), result02.status_code


@main_bp.route('/')
def index():
    return render_template("main.html")


@main_bp.app_errorhandler(404)
def error_404(error):
    return "<h1>404 Not found</h1>", 404
