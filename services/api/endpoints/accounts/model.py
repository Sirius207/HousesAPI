"""
MongoDB Collection Model: Account
"""
from api.db import db


# pylint: disable= E1101
class Account(db.Document):
    username = db.StringField(required=True, primary_key=True, max_length=10)
    user_role = db.StringField(required=True, max_length=5)
    token = db.StringField(required=True, max_length=32)
    month_api_limit = db.IntField(required=True)
    api_quota = db.IntField(required=True)
    key_expire_at = db.DateTimeField(required=True)


# pylint: enable= E1101
