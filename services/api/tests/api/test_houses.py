import json
import pytest

from tests import CLIENT


POST_INPUT = {
    "success": {
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
    },
}

POST_OUTPUT = {
    "success": {
        "status": 200,
        "body": json.dumps({"data": None}),
    }
}

HOUSE_URL = "http://locahost:5000/api/houses"
HOUSE_HEADERS = {"Content-type": "application/json"}


# pylint: disable=W0621
@pytest.mark.parametrize("test_type", POST_INPUT.keys())
def test_house_post(test_type):
    print(POST_INPUT[test_type])
    resp = CLIENT.post(
        HOUSE_URL, headers=HOUSE_HEADERS, data=json.dumps(POST_INPUT[test_type])
    )

    assert resp.status_code == POST_OUTPUT[test_type]["status"]
    resp = json.loads(resp.data.decode())
    test = json.loads(POST_OUTPUT[test_type]["body"])
    assert resp == test


# pylint: enable=W0621

GET_INPUT = {
    "all": {"city": "測試市"},
    "no_data": {"city": "None"},
    "city-renter_gender": {"city": "測試市", "renter_gender": "男"},
    "phone": {"city": "測試市", "phone": "09xxxxxxxx"},
    "lessor_identity": {"city": "測試市", "lessor_identity": "非屋主"},
    "city-lessor_gender-lessor_lastname": {
        "city": "測試市",
        "lessor_gender": "女",
        "lessor_lastname": "李",
    },
}

GET_OUTPUT = {
    "all": {"status": 200, "len": 10},
    "no_data": {"status": 404, "len": 0},
    "city-renter_gender": {"status": 200, "len": 6},
    "phone": {"status": 200, "len": 6},
    "lessor_identity": {"status": 200, "len": 6},
    "city-lessor_gender-lessor_lastname": {"status": 200, "len": 1},
}


@pytest.mark.parametrize("test_type", GET_INPUT.keys())
def test_house_get(test_type):

    resp = CLIENT.get(f"{HOUSE_URL}", query_string=GET_INPUT[test_type])
    assert resp.status_code == GET_OUTPUT[test_type]["status"]

    resp = json.loads(resp.data.decode())
    assert resp["len"] == GET_OUTPUT[test_type]["len"]
