"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import logging
from web_render.config import configuration

config = configuration.get()

def log(name, filename=None):
    # создаём logger
    logger = logging.getLogger(name)
    logger.setLevel(config.LOGGING_LEVEL)

    # создаём консольный handler и задаём уровень
    if filename:
        ch = logging.FileHandler(filename)
    else:
        ch = logging.StreamHandler()

    ch.setLevel(logging.DEBUG)

    # создаём formatter
    formatter = logging.Formatter(
        '%(asctime)s : %(lineno)d : %(name)s : %(levelname)s : %(message)s')
    # %(lineno)d :
    # добавляем formatter в ch
    ch.setFormatter(formatter)

    # добавляем ch к logger
    logger.addHandler(ch)

    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')
    return logger


def merge_args_and_config(args=None, config=None) -> dict:
    data = dict()

    if config:
        all_attributes = {attr: getattr(config, attr) for attr in dir(config) if not callable(getattr(config, attr)) and not attr.startswith('_')}
        data.update(all_attributes)


    if args:
        args_dict = vars(args)
        res = {key.upper(): value for key, value in args_dict.items() if value is not None}
        data.update(res)

    return data
