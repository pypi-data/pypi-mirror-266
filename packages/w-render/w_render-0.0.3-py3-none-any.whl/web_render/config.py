"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import os
import logging
from typing import Union
from dotenv import load_dotenv
load_dotenv()


class BaseEnvironment:
    NAME = "base"
    APP_DIR = os.getenv("APP_DIR", os.getcwd())
    STORAGE = "/tmp"
    SQLITE_PATH = os.path.join(STORAGE, "database.sqlite")
    PRODUCTION = False
    RENDER_ADDRESS = ('localhost', 21000)
    RENDER_AUTH_KEY = b"qwerty"
    CHROME_DRIVER_VERSION = os.environ.get('CHROME_DRIVER_VERSION', '114.0.5735.90')
    LOGGING_LEVEL = logging.DEBUG


class ProductionEnvironment(BaseEnvironment):
    NAME = "production"
    PRODUCTION = True
    LOGGING_LEVEL = logging.INFO


class DevelopmentEnvironment(BaseEnvironment):
    NAME = "development"


class TestingEnvironment(BaseEnvironment):
    NAME = "testing"


class Config:
    _config:Union[
        BaseEnvironment,
        DevelopmentEnvironment,
        ProductionEnvironment,
        TestingEnvironment]  = None

    @staticmethod
    def get(default="production"):
        if Config._config is None:
            return Config()[default]
        return Config._config

    def __init__(self):
        self.config = {
            "development" : DevelopmentEnvironment,
            "testing" : TestingEnvironment,
            "production": ProductionEnvironment
        }

    def __getitem__(self, item):
        config = self.config[item]
        Config._config = config
        return config


configuration = Config()
