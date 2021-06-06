import json
import pytest

from tests import CLIENT
from api.config import Config

VALID_HOUSE_HEADERS = {
    "Content-type": "application/json",
    "Authorization": Config.ADMIN_USER["token"],
}

INVALID_HOUSE_HEADERS = {
    "Content-type": "application/json",
    "Authorization": "wrong_token",
}

VALID_HOUSE_INPUT = {
    "house_id": "11111117",
    "title": "吉屋",
    "city": "桃園市",
    "district": "中和區",
    "lessor": "王先生",
    "lessor_identity": "代理人",
    "house_type": "公寓",
    "house_status": "雅房",
    "sold": None,
    "phone": "09xxxxxxxx",
    "gender_requirement": "男女生皆可",
    "house_condition": "正常",
}

POST_INPUT = {
    "wrong_token": (INVALID_HOUSE_HEADERS, VALID_HOUSE_INPUT),
    "success": (VALID_HOUSE_HEADERS, VALID_HOUSE_INPUT),
}

POST_OUTPUT = {
    "wrong_token": {"status": 403},
    "success": {
        "status": 201,
        "body": json.dumps({"data": None}),
    },
}

HOUSE_URL = "http://locahost:5000/api/houses"


# pylint: disable=W0621
@pytest.mark.parametrize("test_type", POST_INPUT.keys())
def test_house_post(test_type):
    resp = CLIENT.post(
        HOUSE_URL,
        headers=POST_INPUT[test_type][0],
        data=json.dumps(POST_INPUT[test_type][1]),
    )

    assert resp.status_code == POST_OUTPUT[test_type]["status"]
    if resp.status_code == 201:
        resp = json.loads(resp.data.decode())
        test = json.loads(POST_OUTPUT[test_type]["body"])
        assert resp == test


# pylint: enable=W0621

GET_INPUT = {
    "wrong_token": (INVALID_HOUSE_HEADERS, {"city": "測試市"}),
    "all": (VALID_HOUSE_HEADERS, {"city": "測試市"}),
    "no_data": (VALID_HOUSE_HEADERS, {"city": "None"}),
    "city-renter_gender": (VALID_HOUSE_HEADERS, {"city": "測試市", "renter_gender": "男"}),
    "phone": (VALID_HOUSE_HEADERS, {"city": "測試市", "phone": "09xxxxxxxx"}),
    "lessor_identity": (VALID_HOUSE_HEADERS, {"city": "測試市", "lessor_identity": "非屋主"}),
    "city-lessor_gender-lessor_lastname": (
        VALID_HOUSE_HEADERS,
        {
            "city": "測試市",
            "lessor_gender": "女",
            "lessor_lastname": "李",
        },
    ),
}

GET_OUTPUT = {
    "wrong_token": {"status": 403},
    "all": {"status": 200, "len": 10},
    "no_data": {"status": 404, "len": 0},
    "city-renter_gender": {"status": 200, "len": 6},
    "phone": {"status": 200, "len": 6},
    "lessor_identity": {"status": 200, "len": 6},
    "city-lessor_gender-lessor_lastname": {"status": 200, "len": 1},
}


@pytest.mark.parametrize("test_type", GET_INPUT.keys())
def test_house_get(test_type):

    resp = CLIENT.get(
        f"{HOUSE_URL}",
        headers=GET_INPUT[test_type][0],
        query_string=GET_INPUT[test_type][1],
    )
    assert resp.status_code == GET_OUTPUT[test_type]["status"]
    if resp.status_code == 200:
        resp = json.loads(resp.data.decode())
        assert resp["len"] == GET_OUTPUT[test_type]["len"]
