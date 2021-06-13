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

    API_VERSION = os.environ.get("API_VERSION", "v1")
    API_PREFIX = f"/{API_VERSION}/api"

    MONGODB_SETTINGS = {
        "host": os.environ.get("MONGO_HOST", "localhost"),
        "db": os.environ.get("MONGO_DATABASE", "flaskdb"),
        "username": os.environ.get("MONGO_DB_USERNAME", "apiuser"),
        "password": os.environ.get("MONGO_DB_PASSWORD", "sample"),
    }

    # API Account
    ADMIN_USER = {
        "username": os.environ.get("ADMIN_USER_NAME", "admin"),
        "token": os.environ.get("ADMIN_USER_TOKEN"),  # uuid
    }

    ELASTIC_APM = {
        "SERVICE_NAME": "house-api",
        "SERVER_URL": "http://localhost:8200",
        "DEBUG": True,
        "SECRET_TOKEN": os.environ.get("APM_TOKEN"),
        "TRACES_SEND_FREQ": 5,
        "FLUSH_INTERVAL": 1,
        "MAX_QUEUE_SIZE": 1,
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
    Config.ELASTIC_APM["DEBUG"] = False


APP_CONFIG = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}
