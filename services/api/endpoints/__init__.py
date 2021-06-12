"""
Organize all API entrypoints
Author: Po-Chun, Lu

"""
from api.endpoints.houses.resource import HousesOperator
from api.endpoints.accounts.resource import AccountsOperator
from api.config import Config


RESOURCES = {
    f"{Config.API_PREFIX}/houses": HousesOperator,
    f"{Config.API_PREFIX}/accounts": AccountsOperator,
}
