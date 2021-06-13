"""
Module for /api/house method
"""
import json
from typing import Dict, Tuple

import elasticapm
from flask_restful import Resource, reqparse

from api.endpoints.houses.model import House
from api.endpoints.utils import add_common_arguments, add_auth_argument, log_context
from api.endpoints.accounts.auth import authorization_validator


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
            if args["house_status"] == "非車位":
                query_conditions["house_status__nin"] = ("車位",)
            else:
                query_conditions["house_status"] = args["house_status"]

        gender_map = {"男": ("男女生皆可", "男生"), "女": ("男女生皆可", "女生")}
        if args["renter_gender"] and args["renter_gender"] in gender_map:
            query_conditions["gender_requirement__in"] = gender_map[
                args["renter_gender"]
            ]

        if args["lessor_identity"]:
            if args["lessor_identity"] == "屋主":
                query_conditions["lessor_identity__in"] = ("屋主", "屋主聲明：仲介勿擾")
            elif args["lessor_identity"] == "代理人":
                query_conditions["lessor_identity__contains"] = "代理人"
            elif args["lessor_identity"] == "非屋主":
                query_conditions["lessor_identity__nin"] = ("屋主", "屋主聲明：仲介勿擾")
            elif args["lessor_identity"] == "仲介":
                query_conditions["lessor_identity__in"] = "仲介，收取服務費"

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
