"""
Module for /api/house method
"""
import json
from typing import Dict, Tuple

import elasticapm
from flask_restful import Resource, reqparse

from api.endpoints.accounts.auth import authorization_validator
from api.endpoints.houses.model import House
from api.endpoints.utils import add_auth_argument, add_common_arguments, log_context


class HousesOperator(Resource):
    def __init__(self):
        self.model = House
        self._set_get_parser()
        self._set_post_parser()

    def _set_get_parser(self):
        self.get_parser = reqparse.RequestParser()
        add_common_arguments(
            self.get_parser,
            "values",
            (
                ("renter_gender", False),
                ("city", False),
                ("district", False),
                ("house_type", False),
                ("house_status", False),
                ("phone", False),
                ("lessor_identity", False),
                ("lessor_gender", False),
                ("lessor_lastname", False),
                ("explain", False),
            ),
        )

        add_auth_argument(self.get_parser)

    @staticmethod
    def _get_fields(document_object):

        return json.loads(document_object.to_json())

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()

        add_common_arguments(
            self.post_parser,
            "json",
            (
                ("house_id", True),
                ("title", True),
                ("city", True),
                ("district", True),
                ("lessor", True),
                ("lessor_gender", False),
                ("lessor_identity", True),
                ("house_type", False),
                ("house_status", False),
                ("sold", False),
                ("phone", True),
                ("gender_requirement", False),
                ("house_condition", True),
            ),
        )

        add_auth_argument(self.post_parser)

    @staticmethod
    def _query_conditions(args) -> dict:
        query_conditions = {}

        for query_param in ("city", "district", "phone", "house_type", "lessor_gender"):
            if args[query_param]:
                query_conditions[query_param] = args[query_param]

        if args["house_status"]:
            if args["house_status"] == "?????????":
                query_conditions["house_status__nin"] = ("??????",)
            else:
                query_conditions["house_status"] = args["house_status"]

        gender_map = {"???": ("???????????????", "??????"), "???": ("???????????????", "??????")}
        if args["renter_gender"] and args["renter_gender"] in gender_map:
            query_conditions["gender_requirement__in"] = gender_map[
                args["renter_gender"]
            ]

        if args["lessor_identity"]:
            if args["lessor_identity"] == "??????":
                query_conditions["lessor_identity__in"] = ("??????", "???????????????????????????")
            elif args["lessor_identity"] == "?????????":
                query_conditions["lessor_identity__contains"] = "?????????"
            elif args["lessor_identity"] == "?????????":
                query_conditions["lessor_identity__nin"] = ("??????", "???????????????????????????")
            elif args["lessor_identity"] == "??????":
                query_conditions["lessor_identity__in"] = ("????????????????????????", "??????")

        if args["lessor_lastname"]:
            query_conditions["lessor__contains"] = args["lessor_lastname"]

        return query_conditions

    def _get_data(self, query_conditions: dict) -> Tuple[Dict[str, object], int]:
        # pylint: disable= E1101
        houses = House.objects(**query_conditions)
        # pylint: enable= E1101
        if not houses:
            return {"message": "not found", "len": 0, "data": []}, 404

        return (
            {
                "message": "success",
                "len": houses.count(),
                "data": [self._get_fields(house) for house in houses],
            },
            200,
        )

    @staticmethod
    def _get_explain(query_conditions: dict) -> Tuple[Dict[str, object], int]:
        # pylint: disable= E1101
        explain = House.objects(**query_conditions).explain()
        # pylint: enable= E1101
        return ({"message": "success", "explain": explain}, 200)

    @elasticapm.capture_span()
    @authorization_validator("user")
    def get(self) -> Tuple[Dict[str, object], int]:
        """the GET /api/houses method

        Returns:
            Tuple[Dict[str, object], int]: (response body, http status)
        """
        args = self.get_parser.parse_args()

        query_conditions = self._query_conditions(args)

        if args["explain"] == "on":
            return self._get_explain(query_conditions)

        return self._get_data(query_conditions)

    @elasticapm.capture_span()
    @authorization_validator("admin")
    def post(self) -> Tuple[Dict[str, object], int]:
        """the POST /api/houses method

        Returns:
            Tuple[Dict[str, object], int]: (response body, http status)
        """
        args = self.post_parser.parse_args()
        del args["Authorization"]
        log_context("Request - Body", args)
        House(**args).save()
        return ({"data": None}, 201)
