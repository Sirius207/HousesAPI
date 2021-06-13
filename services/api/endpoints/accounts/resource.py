"""
Module for /api/account method
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple

from flask_restful import Resource, reqparse
from werkzeug.exceptions import abort

from api.endpoints.accounts.auth import authorization_validator
from api.endpoints.accounts.model import Account
from api.endpoints.utils import add_auth_argument, add_common_arguments, log_context


class AccountsOperator(Resource):
    def __init__(self):
        self.model = Account
        self._set_post_parser()

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()

        add_common_arguments(
            self.post_parser, "json", (("username", True), ("user_role", True))
        )

        add_auth_argument(self.post_parser)

    @authorization_validator("admin")
    def post(self) -> Tuple[Dict[str, object], int]:
        """the POST /api/account method

        Returns:
            Tuple[Dict[str, object], int]: (response body, http status)
        """
        args = self.post_parser.parse_args()
        log_context("Request - Body", args)

        if Account.objects(username=args["username"]):
            abort(400, "username exists")

        if args["user_role"] not in ("admin", "user"):
            abort(400, "invalid user_role")

        if args["user_role"] == "admin":
            month_api_limit = 5000
            api_quota = 5000
            key_expire_at = datetime.utcnow() + timedelta(days=365)
        else:
            month_api_limit = 1000
            api_quota = 1000
            key_expire_at = datetime.utcnow() + timedelta(days=30)

        new_account = {
            "username": args["username"],
            "user_role": args["user_role"],
            "token": uuid.uuid4().hex,
            "month_api_limit": month_api_limit,
            "api_quota": api_quota,
            "key_expire_at": key_expire_at,
        }

        Account(**new_account).save()

        new_account["key_expire_at"] = new_account["key_expire_at"].strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        return ({"message": "success", "data": new_account}, 200)
