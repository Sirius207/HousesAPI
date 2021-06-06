from datetime import datetime
from typing import Callable

from loguru import logger
from werkzeug.exceptions import abort

from api.endpoints.accounts.model import Account


def _valid_token(token: str, user_role):

    account = Account.objects(token=token).first()
    # 1. account exist
    if not account:
        logger.warning(f"Authorization token {token} not found")
        abort(403, "Forbiden")

    # 2. valid user role
    if account.user_role != user_role and account.user_role != "admin":
        logger.warning(f"Authorization expect admin, get {account.user_role}")
        abort(403, "Forbiden")

    # 3. valid token time
    current_time = datetime.utcnow().timestamp()
    expired_time = account.key_expire_at.timestamp()
    if current_time - expired_time > 0:
        logger.warning(f"Authorization expired: {current_time} > {expired_time}")
        abort(403, "Forbiden")

    # 4. valid quota
    if account.api_quota > 0:
        account.api_quota -= 1
        account.save()
    else:
        abort(403, "No quota this month")


def authorization_validator(user_role) -> Callable:
    def decorator(func) -> Callable:
        def wrapper(req_object) -> Callable:
            args = req_object.get_parser.parse_args()
            _valid_token(args["Authorization"], user_role)
            return func(req_object)

        return wrapper

    return decorator
