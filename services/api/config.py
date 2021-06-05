"""
Module of flask config
Author: Po-Chun, Lu

"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Parent configuration class."""

    DEBUG = False
    CSRF_ENABLED = True
    DATE_TIME = "%Y-%m-%dT%H:%M:%S"
    TIME_ZONE = os.environ.get("TIME_ZONE", 8)

    MONGODB_SETTINGS = {
        "host": os.environ.get("MONGO_HOST", "localhost"),
        "db": os.environ.get("MONGO_DATABASE", "flaskdb"),
        "username": os.environ.get("MONGO_DB_USERNAME", "apiuser"),
        "password": os.environ.get("MONGO_DB_PASSWORD", "sample"),
    }


class DevelopmentConfig(Config):
    """ "configuration class for dev env"""

    DEBUG = True


class TestingConfig(Config):
    """ "configuration class for testing env"""

    TESTING = True
    DEBUG = True


class StagingConfig(Config):
    """ "configuration class for staging env"""

    DEBUG = True


class ProductionConfig(Config):
    """ "configuration class for prod env"""

    DEBUG = False
    TESTING = False


APP_CONFIG = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}
