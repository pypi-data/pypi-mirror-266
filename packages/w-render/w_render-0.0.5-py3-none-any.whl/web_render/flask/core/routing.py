"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from .main.view import main_bp
from .render_api.view import render_api_bp

blueprint_list = [main_bp, render_api_bp]