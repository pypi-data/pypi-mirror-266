"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import os
import argparse
from web_render.tool import merge_args_and_config
import importlib

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, description='Example: ***')
    parser.add_argument('-c', '--config', dest='config', type=str, default="production")
    parser.add_argument('--config-path', dest='config_path', type=str, default="web_render.config")
    parser.add_argument('--port', dest='port', type=int, default=5000)

    def render_address(string):
        if string == "None":
            return None
        address, port = string.split(":")
        return (address, int(port))

    parser.add_argument('--render-address', dest='render_address', type=render_address, default="None")
    return parser.parse_args()


def create_app(args, config):
    from flask import Flask

    app = Flask(__name__, static_folder="core/main/static", template_folder="templates")
    app.secret_key = os.urandom(24)

    config_dict = merge_args_and_config(args, config)
    app.config.update(config_dict)

    from web_render.flask.core.routing import blueprint_list
    [app.register_blueprint(x) for x in blueprint_list]
    return app


def cli():
    args = parse_arguments()

    config_module = importlib.import_module(f'{args.config_path}')
    configuration = config_module.configuration

    config = configuration[args.config]
    app = create_app(args, config)

    if args.config == "testing" or args.config == "development":
        app.run(port=args.port, host='0.0.0.0', debug=False)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=args.port)


if __name__ == '__main__':
    cli()

