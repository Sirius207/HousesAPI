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

    @staticmethod
    def _get_fields(document_object):
        api_result = json.loads(document_object.to_json())

        hide_fields = ("_id",)
        for hide_field in hide_fields:
            del api_result[hide_field]
        return api_result

    def _set_post_parser(self):
        self.post_parser = reqparse.RequestParser()

        add_common_arguments(
            self.post_parser,
            (
                ("url", True),
                ("title", True),
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

    def get(self):
        houses = House.objects()
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
