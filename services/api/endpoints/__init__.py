"""
Organize all API entrypoints
Author: Po-Chun, Lu

"""
from api.config import Config
from api.endpoints.accounts.resource import AccountsOperator
from api.endpoints.houses.resource import HousesOperator

RESOURCES = {
    f"{Config.API_PREFIX}/houses": HousesOperator,
    f"{Config.API_PREFIX}/accounts": AccountsOperator,
}
