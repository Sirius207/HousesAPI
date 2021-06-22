"""
Module for houses detailed data parsing
"""
import os
import re
import uuid
from typing import Optional, Tuple

from loguru import logger
from requests_html import HTMLSession
from bs4 import BeautifulSoup

logger.add("house_parse.log", level="DEBUG")


# pylint: disable= R0902


class House:
    def __init__(self, url: str, title: str, data):
        self.url = url
        self.title = title

        self.phone = data["linkInfo"]["mobile"]
        self.city = data["breadcrumb"][0]["name"].replace("租屋", "市")
        self.district = data["breadcrumb"][1]["name"].replace("租屋", "市")
        self.house_status = data["breadcrumb"][2]["name"].replace("租屋", "市")

        self.lessor, self.lessor_gender, self.lessor_identity = self._get_lessor_info(
            data
        )

        self.sold = None
        self.house_type = self._get_house_type(data)
        self.gender_requirement = self._get_gender_requirement(data)
        self.house_condition = self._get_house_condition(data)

    @staticmethod
    def _get_lessor_info(data) -> Tuple:
        """[summary]

        Args:
            html ([type]): [description]

        Returns:
            Tuple: [description]
        """
        lessor_gender: Optional[str] = None
        lessor_identity: Optional[str] = None

        lessor = data["linkInfo"]["name"]
        pattern_after_colon = r":\s*(.*)"
        lessor = re.findall(pattern_after_colon, lessor)[0].strip()

        lessor_identity = data["linkInfo"]["name"].replace(f": {lessor}", "")
        if lessor:
            if "先生" in lessor:
                lessor_gender = "男"
            elif "小姐" in lessor:
                lessor_gender = "女"

        return lessor, lessor_gender, lessor_identity

    @staticmethod
    def _get_house_type(data) -> Optional[str]:
        """parse the "型態" value from house page

        Args:
            html (object): the html object generate by request_html

        Returns:
            Optional[str]: the "型態" field. e.g. "電梯大樓"
        """

        for item in data["infoData"]["data"]:
            if item["name"] == "型態":
                return item["value"]

        return None

    @staticmethod
    def _get_gender_requirement(data) -> Optional[str]:
        """parse the "性別要求" value from house page

        Args:
            html ([type]): the html object generate by request_html

        Returns:
            Optional[str]: the "性別要求" value. e.g. "男女生皆可"
        """
        rule = data["service"]["rule"]

        if "限男生" in rule:
            return "男生"
        if "限女生" in rule:
            return "女生"
        return "男女生皆可"

    @staticmethod
    def _get_house_condition(data) -> Optional[str]:
        """parse the "屋況說明" value from house page

        Args:
            html ([type]): the html object generate by request_html

        Returns:
            Optional[str]: the "屋況說明" value
        """
        house_condition = data["remark"]["content"]
        soup = BeautifulSoup(house_condition, features="html.parser")
        return soup.get_text() if house_condition else None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "city": self.city,
            "district": self.district,
            "lessor": self.lessor,
            "lessor_gender": self.lessor_gender,
            "lessor_identity": self.lessor_identity,
            "house_type": self.house_type,
            "house_status": self.house_status,
            "sold": self.sold,
            "phone": self.phone,
            "gender_requirement": self.gender_requirement,
            "house_condition": self.house_condition,
        }


# pylint: enable= R0902


def parse_single_house(url, title, proxy=None) -> Optional[dict]:
    """[summary]

    Args:
        url ([type]): the url of this house
        title ([type]): the title of this house
        proxy ([type], optional): the proxy IP. Defaults to None.

    Returns:
        Optional[dict]: the house detailed data
    """
    session_arg = {"browser_args": [f"--proxy-server={proxy}"]} if proxy else {}
    headers = {
        "device": "pc",
        "deviceid": str(uuid.uuid4()),
    }
    house_id = url.replace(os.environ.get("WEB_URL_PREFIX"), "").replace(".html", "")
    url = f"{os.environ.get('API_WEB_URL')}/tw/v1/house/rent/detail?id={house_id}&isOnline=1"
    res = HTMLSession(**session_arg).get(url, headers=headers)
    status = res.status_code
    logger.info(f"Parse: {url} {status}")
    if status != 200:
        logger.error(status, res.text)
        return None

    try:
        return House(url, title, res.json()["data"]).to_dict()
    except AttributeError as error:
        logger.warning(f"{url}\n{error}")
        return None
