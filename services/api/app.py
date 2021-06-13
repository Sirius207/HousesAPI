"""
Entry Module
Author: Po-Chun, Lu

"""
import logging
import os
import sys

from dotenv import load_dotenv
from elasticapm.contrib.flask import ElasticAPM
from flask import Flask
from flask_restful import Api
from werkzeug.exceptions import HTTPException, default_exceptions


from config import APP_CONFIG
from db import db
from endpoints import RESOURCES
from endpoints.utils import log_context

load_dotenv()


def create_app(config_mode):
    """main function of flask app"""

    app = Flask(__name__)

    # silent flask, werkzeug log level
    # pylint: disable= E1101
    app.logger.setLevel(logging.ERROR)
    # pylint: enable= E1101
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.ERROR)

    @app.errorhandler(Exception)
    def handle_error(error):
        code = 500

        if isinstance(error, HTTPException):
            code = error.code

        return {"error": str(error)}, code

    for ex in default_exceptions:
        app.register_error_handler(ex, handle_error)

    # flask config
    app.config.from_object(APP_CONFIG[config_mode])

    db.init_app(app)
    ElasticAPM(app, logging=True)

    # Route Init
    api = Api(app)
    for route in RESOURCES:
        api.add_resource(RESOURCES[route], route)

    # create logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s+%(tz)02d:00]"
        " [houses-api]"
        " [%(levelname)s]"
        " [%(resource)s - %(ip)s]"
        " [%(method)s]"
        ' Path: "%(path)s"'
        " | Content: %(message)s"
    )
    logger.handlers = []
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # pylint: disable=W0612
    @app.before_request
    def before_request_callback():
        """log before request"""
        log_context("Request")

    @app.after_request
    def after_request_callback(response):
        """log after request"""
        response_dict = response.get_json()
        response_dict["status_code"] = response.status_code

        log_context("Response", response_dict)
        return response

    # pylint: enable=W0612

    return app


def main():
    """main function for defining flask app"""
    config_name = os.environ.get("APP_SETTINGS", "development")

    app = create_app(config_name)
    app.run(host=os.environ.get("HOST"))


if __name__ == "__main__":
    main()
