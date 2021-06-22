"""
Module for create default api user with token
"""

from datetime import datetime, timedelta

from loguru import logger

from api.config import Config
from api.endpoints.accounts.model import Account
from api.loader.csv_to_mongo import connect_mongo


def create_init_api_account():
    connect_mongo()

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
