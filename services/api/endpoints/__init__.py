"""
Organize all API entrypoints
Author: Po-Chun, Lu

"""
from api.endpoints.houses.resource import HousesOperator
from api.endpoints.accounts.resource import AccountsOperator

RESOURCES = {
    "/api/houses": HousesOperator,
    "/api/accounts": AccountsOperator,
}
