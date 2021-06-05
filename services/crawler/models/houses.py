import re
from typing import Optional, Tuple

import pytesseract
from loguru import logger
from PIL import Image, ImageEnhance
from requests_html import HTMLSession
from selenium.common.exceptions import NoSuchElementException

from crawler.utils.driver import get_driver


class PhoneOperator:
    @classmethod
    def get_phone_from_url(cls, url: str, html) -> Optional[str]:

        # Method 1. Read Phone Text
        phone = cls._get_phone_from_text(html)
        if phone:
            return phone

        # Method 2. recognize image directly
        phone = cls._get_phone_from_image(html)

        # Method 3. recognize image from screenshot
        if not phone or not cls._validate_phone_str(phone):
            logger.warning(f"{url}: image detect: {phone} -> parse screenshot ")
            phone = cls._get_phone_from_screenshot(url)

        if not phone or not cls._validate_phone_str(phone):
            logger.error(f"{url}: parse screenshot -> {phone}")
        else:
            logger.success(f"{url}: parse screenshot -> {phone}")

        return phone

    @classmethod
    def _get_phone_from_image(cls, html) -> Optional[str]:
        image_element = html.find(".num img", first=True)
        if not image_element:
            return None
        image_url = f'https:{image_element.attrs["src"]}'
        session = HTMLSession()
        image = Image.open(session.get(image_url, stream=True).raw)

        image = image.convert("L")
        image = ImageEnhance.Brightness(image).enhance(0.5)

        return cls._image_to_phone(image)

    @staticmethod
    def _image_to_phone(image) -> str:
        # resize
        image = image.resize((360, 60))

        return (
            pytesseract.image_to_string(image)
            .replace("\n\x0c", "")
            .replace(" ", "")
            .replace("-", "")
        )

    @staticmethod
    def _validate_phone_str(phone: str) -> bool:
        try:
            return bool(int(phone))
        except ValueError as error:
            logger.warning(error)
            return False

    @classmethod
    def _get_phone_from_screenshot(cls, url: str) -> Optional[str]:
        # pick house_id from url string
        house_id = url[-13:-5]
        screen_file = f"./data/phone/full_{house_id}.png"
        phone_img = cls._save_screenshot(screen_file, url)

        if phone_img:
            return cls._recognize_phone_image(screen_file, phone_img)

        return None

    @staticmethod
    def _save_screenshot(screen_file: str, url: str) -> Optional[str]:
        try:
            driver = get_driver()
            driver.set_window_size(1366, 768)
            driver.get(url)
            driver.save_screenshot(screen_file)

            return driver.find_element_by_css_selector(".num img")
        except NoSuchElementException as error:
            logger.warning(f"{url} phone image not found\n{error}")
            return None

    @classmethod
    def _recognize_phone_image(cls, screen_file: str, phone_img):

        # calc phone position
        location = phone_img.location
        size = phone_img.size
        phone_img_x = location["x"]
        phone_img_y = location["y"]
        height = phone_img_y + size["height"]
        width = phone_img_x + size["width"]

        # crop photo
        image = Image.open(screen_file)
        image = image.crop((phone_img_x, phone_img_y, int(width), int(height)))

        return cls._image_to_phone(image)

    @staticmethod
    def _get_phone_from_text(html) -> Optional[str]:
        phone = html.find(".num", first=True)
        if phone:
            return phone.text

        return None


# pylint: disable= R0902


class House:
    def __init__(self, url: str, title: str, html):
        self.url = url
        self.title = title
        self.sold = (
            html.find(".DealEnd", first=True).text if html.find(".DealEnd") else None
        )
        self.phone = (
            PhoneOperator.get_phone_from_url(url, html) if not self.sold else None
        )
        nav = html.find("#propNav a")
        self.city = nav[2].text
        self.district = nav[3].text
        self.house_status = nav[4].text

        self.lessor, self.lessor_gender, self.lessor_identity = self._get_lessor_info(
            html
        )

        self.house_type = self._get_house_type(html)
        self.gender_requirement = self._get_gender_requirement(html)

        self.house_condition = self._get_house_condition(html)

    @staticmethod
    def _get_lessor_info(html) -> Tuple:
        lessor_gender: Optional[str]
        lessor_identity: Optional[str]

        lessor = html.find(".avatarRight i", first=True)
        if lessor:
            lessor = lessor.text
            if "先生" in lessor:
                lessor_gender = "男"
            elif "小姐" in lessor:
                lessor_gender = "女"
            # e.g. pick "代理人" from "蘇先生（代理人）"
            lessor_identity = html.find(".avatarRight div", first=True).text.replace(
                lessor, ""
            )[1:-1]
        else:
            lessor = lessor_gender = lessor_identity = None

        return lessor, lessor_gender, lessor_identity

    @staticmethod
    def _get_house_type(html) -> Optional[str]:
        elements = html.find(".attr li")

        house_type = None
        for element in elements:
            pattern_after_colon = r":\s*(.*)"
            if "型" in element.text:
                house_type = re.findall(
                    pattern_after_colon, element.text.replace("\n", "")
                )[0]

        return house_type

    @staticmethod
    def _get_gender_requirement(html) -> Optional[str]:
        elements = html.find("ul li.clearfix .one")
        labels = [element.text.replace("\n", "").strip() for element in elements]
        try:
            index = labels.index("性別要求")
            elements = html.find("ul li.clearfix .two em")
            return elements[index].text.replace("\n", "")
        except ValueError:
            return None

    @staticmethod
    def _get_house_condition(html) -> Optional[str]:
        house_condition = html.find(".houseIntro", first=True)
        return house_condition.text if house_condition else None

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
    session_arg = {"browser_args": [f"--proxy-server={proxy}"]} if proxy else {}

    res = HTMLSession(**session_arg).get(url)

    if res.html.find(".error_img") or res.html.find("#error-page"):
        logger.warning(f"{url} house was removed")
        return None

    try:
        return House(url, title, res.html).to_dict()
    except AttributeError as error:
        logger.warning(f"{url}\n{error}")
        return None
