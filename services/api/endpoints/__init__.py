"""
Organize all API entrypoints
Author: Po-Chun, Lu

"""
from endpoints.houses.resource import HousesOperator

RESOURCES = {"/api/houses": HousesOperator}
