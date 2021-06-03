import re
from typing import Optional, Tuple

from requests_html import HTMLSession
from PIL import Image, ImageEnhance
import pytesseract
from loguru import logger
from selenium.common.exceptions import NoSuchElementException

from crawler.utils.driver import get_driver


class PhoneOperator:
    @classmethod
    def get_phone_from_url(cls, url: str, html) -> Optional[str]:
        phone = cls._get_phone_from_text(html)
        if not phone:
            phone = cls._get_phone_from_image(html)
        if not phone:
            phone = cls._get_phone_from_screenshot(url)

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
        image = image.resize((360, 60))

        return pytesseract.image_to_string(image).replace("\n\x0c", "")

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
        except NoSuchElementException as e:
            logger.warning(f"{url} phone image not found\n{e}")
            return None

    @staticmethod
    def _recognize_phone_image(screen_file: str, phone_img):

        # calc phone position
        location = phone_img.location
        size = phone_img.size
        x = location["x"]
        y = location["y"]
        height = y + size["height"]
        width = x + size["width"]

        # crop photo
        imgOpen = Image.open(screen_file)
        imgOpen = imgOpen.crop((x, y, int(width), int(height)))

        # resize
        image = imgOpen
        image = image.resize((360, 60))
        return pytesseract.image_to_string(image).replace("\n\x0c", "")

    @staticmethod
    def _get_phone_from_text(html) -> Optional[str]:
        phone = html.find(".num", first=True)
        if phone:
            return phone.text

        return None


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

        self.lessor, self.lessor_identity = self._get_lessor_info(html)

        self.house_type, self.house_status = self._get_house_info(html)
        self.gender_requirement = self._get_gender_requirement(html)

        self.house_condition = self._get_house_condition(html)

    @staticmethod
    def _get_lessor_info(html) -> Tuple:
        lessor = html.find(".avatarRight i", first=True)
        if lessor:
            lessor = lessor.text
            lessor_identity = html.find(".avatarRight", first=True).text.replace(
                lessor, ""
            )
        else:
            lessor = None
            lessor_identity = None

        return lessor, lessor_identity

    @staticmethod
    def _get_house_info(html) -> Tuple:
        elements = html.find(".attr li")

        house_type = house_status = None
        for element in elements:
            pattern_after_colon = r":\s*(.*)"
            if "型" in element.text:
                house_type = re.findall(
                    pattern_after_colon, element.text.replace("\n", "")
                )[0]
            elif "現" in element.text:
                house_status = re.findall(
                    pattern_after_colon, element.text.replace("\n", "")
                )[0]

        return house_type, house_status

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
            "lessor": self.lessor,
            "lessor_identity": self.lessor_identity,
            "house_type": self.house_type,
            "house_status": self.house_status,
            "sold": self.sold,
            "phone": self.phone,
            "gender_requirement": self.gender_requirement,
            "house_condition": self.house_condition,
        }


def parse_single_house(url, title, proxy=None) -> Optional[dict]:
    session_arg = {"browser_args": [f"--proxy-server={proxy}"]} if proxy else {}

    r = HTMLSession(**session_arg).get(url)

    if r.html.find(".error_img") or r.html.find("#error-page"):
        logger.warning(f"{url} house was removed")
        return None

    try:
        return House(url, title, r.html).to_dict()
    except AttributeError as e:
        logger.warning(f"{url}\n{e}")
        return None
