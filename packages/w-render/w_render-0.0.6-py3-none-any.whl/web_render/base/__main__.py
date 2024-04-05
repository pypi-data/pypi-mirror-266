"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import argparse
from web_render.config import configuration
from web_render.base.abstract import make_selenium_webdriver, SeleniumRender
from web_render.base.server import ServerRender
from web_render.tool import merge_args_and_config


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Example:\n'
                    'python -m backend.web_render -f server_run -c development\n'
                    '======='
    )
    parser.add_argument('-c', '--config', dest='config', type=str, default="development",
                        help='An example:\npython -m backend.http_server -c development|testing|production')
    parser.add_argument('-f', '--function', dest='function', type=str, required=True)
    parser.add_argument('--address', dest='address', type=str, default="localhost")
    parser.add_argument('--port', dest='port', type=int, default=21000)
    parser.add_argument('--headless', dest='headless', action='store_true', default=False)
    parser.add_argument('--undetected-chromedriver', dest='undetected_chromedriver', action='store_true', default=False)
    parser.add_argument('--proxy', dest='proxy_server', type=str, default=None)
    parser.add_argument('--chrome-driver-version', dest='chrome_driver_version', type=str, default=None)

    return parser.parse_args()


def selenium_render(args, config):
    config_dict = merge_args_and_config(args, config)
    browser = make_selenium_webdriver(config_dict)
    ServerRender(
        SeleniumRender(browser)
    ).run(address=(args.address, args.port), authkey=b'qwerty')



function = {
    "selenium": selenium_render
}


def cli():
    args = parse_arguments()
    config = configuration[args.config]
    function[args.function](args, config)


if __name__ == '__main__':
    cli()