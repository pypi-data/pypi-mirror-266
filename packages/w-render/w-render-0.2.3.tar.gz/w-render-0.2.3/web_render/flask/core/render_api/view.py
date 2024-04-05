"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from flask import Blueprint, jsonify, request, current_app
from .logic import open_page, get_live_content, get_content


render_api_bp = Blueprint('render_api', __name__, url_prefix="/render/api")


@render_api_bp.route('/page/open', methods=['POST'])
def page_open():
    form = request.json  # Получаем URL страницы из POST-запроса
    data = open_page(form, current_app.config['RENDER_ADDRESS'], current_app.config['RENDER_AUTH_KEY'])
    return jsonify(data)


@render_api_bp.route('/page/<string:page_id>', methods=['GET'])
def page_content(page_id):
    data = get_content(page_id, current_app.config['RENDER_ADDRESS'], current_app.config['RENDER_AUTH_KEY'])
    return jsonify(data)


@render_api_bp.route('/page/live', methods=['POST'])
def page_live_content():
    form = request.json
    data = get_live_content(
        form,
        current_app.config['RENDER_ADDRESS'],
        current_app.config['RENDER_AUTH_KEY']
    )
    return jsonify(data)