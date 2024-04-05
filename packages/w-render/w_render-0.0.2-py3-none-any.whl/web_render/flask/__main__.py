"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import os
import argparse
from web_render.tool import merge_args_and_config


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Example: ***')
    parser.add_argument('-c', '--config', dest='config', type=str, default="production",
                        help='--config development|testing|default')
    parser.add_argument('--port', dest='port', type=int, default=5000)
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


def run_develop(app):
    app.run(port=app.config['PORT'], host='0.0.0.0', debug=False)


def run_production(app):
    from waitress import serve
    serve(app, host='0.0.0.0', port=app.config['PORT'])


def cli():
    args = parse_arguments()

    from web_render.config import configuration
    config = configuration[args.config]

    Application = create_app(args, config)

    if args.config == "testing" or args.config == "development":
        run_develop(Application)
    else:
        run_production(Application)


if __name__ == '__main__':
    cli()

