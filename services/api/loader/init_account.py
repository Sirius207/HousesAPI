"""
Module for create default api user with token
"""

from datetime import datetime, timedelta

from api.endpoints.accounts.model import Account
from api.config import Config

from mongoengine import connect
from loguru import logger


def create_init_api_account():
    connect(
        db=Config.MONGODB_SETTINGS["db"],
        host=Config.MONGODB_SETTINGS["host"],
        username=Config.MONGODB_SETTINGS["username"],
        password=Config.MONGODB_SETTINGS["password"],
        port=27017,
    )

    Account(
        **{
            "username": Config.ADMIN_USER["username"],
            "user_role": "admin",
            "token": Config.ADMIN_USER["token"],
            "month_api_limit": 5000,
            "api_quota": 5000,
            "key_expire_at": datetime.utcnow() + timedelta(days=365),
        }
    ).save()
    logger.success("Create New API User")


if __name__ == "__main__":
    create_init_api_account()
