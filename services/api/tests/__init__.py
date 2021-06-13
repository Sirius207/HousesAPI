import os

from app import create_app


def client():
    app = create_app(os.environ.get("APP_SETTINGS", "testing"))
    with app.app_context():
        return app.test_client()


CLIENT = client()
HOST = "http://localhost:5000"
