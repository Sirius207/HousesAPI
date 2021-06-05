import json

from flask_restful import Resource, reqparse

from endpoints.houses.model import House
from endpoints.utils import add_common_arguments, log_context


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
            ),
        )

    @staticmethod
    def _get_fields(document_object):

        return json.loads(document_object.to_json())

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()

        add_common_arguments(
            self.post_parser,
            "values",
            (
                ("house_id", True),
                ("title", True),
                ("city", True),
                ("district", True),
                ("lessor", True),
                ("lessor_identity", True),
                ("house_type", False),
                ("house_status", False),
                ("sold", False),
                ("phone", True),
                ("gender_requirement", False),
                ("house_condition", True),
            ),
        )

    @staticmethod
    def _query_conditions(args) -> dict:
        query_conditions = {}
        if args["city"]:
            query_conditions["city"] = args["city"]
        if args["district"]:
            query_conditions["district"] = args["district"]
        if args["phone"]:
            query_conditions["phone"] = args["phone"]
        if args["house_type"]:
            query_conditions["house_type"] = args["house_type"]
        if args["house_status"]:
            if args["house_status"] == "非車位":
                query_conditions["house_status__nin"] = ("車位",)
            else:
                query_conditions["house_status"] = args["house_status"]

        if args["renter_gender"]:
            if args["renter_gender"] == "男":
                query_conditions["gender_requirement__in"] = ("男女生皆可", "男生")
            elif args["renter_gender"] == "女":
                query_conditions["gender_requirement__in"] = ("男女生皆可", "女生")

        if args["lessor_identity"]:
            if args["lessor_identity"] == "屋主":
                query_conditions["lessor_identity__in"] = ("屋主", "屋主聲明：仲介勿擾")
            elif args["lessor_identity"] == "代理人":
                query_conditions["lessor_identity__contains"] = "代理人"
            elif args["lessor_identity"] == "非屋主":
                query_conditions["lessor_identity__nin"] = ("屋主", "屋主聲明：仲介勿擾")
            elif args["lessor_identity"] == "仲介，收取服務費":
                query_conditions["lessor_identity__in"] = "仲介，收取服務費"

        if args["lessor_gender"]:
            lessor_gender = {"女": "小姐", "男": "先生"}
            query_conditions["lessor__contains"] = lessor_gender[args["lessor_gender"]]

        if args["lessor_lastname"]:
            query_conditions["lessor__contains"] = args["lessor_lastname"]

        return query_conditions

    def get(self):
        args = self.get_parser.parse_args()
        query_conditions = self._query_conditions(args)
        houses = House.objects(**query_conditions)
        if not houses:
            return {
                "message": "not found",
                "len": 0,
                "data": [],
            }, 404

        return {
            "message": "success",
            "len": houses.count(),
            "data": [self._get_fields(house) for house in houses],
        }, 200

    def post(self):
        args = self.post_parser.parse_args()
        log_context("Request - Body", args)

        House(**args).save()
        return ({"data": None}, 200)
