"""
Organize all API entrypoints
Author: Po-Chun, Lu

"""
from api.endpoints.houses.resource import HousesOperator

RESOURCES = {"/api/houses": HousesOperator}
