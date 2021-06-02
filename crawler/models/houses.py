import re
from typing import Optional, Tuple

from joblib import Parallel, delayed
from requests_html import HTMLSession
from PIL import Image
import pytesseract
import pandas as pd
from loguru import logger

from crawler.utils.driver import get_driver


class PhoneOperator:
    @classmethod
    def get_phone_from_url(cls, url: str, html) -> str:
        phone = cls._get_phone_from_text(html)
        if not phone:
            phone = cls._get_phone_from_image(url)

        return phone

    @classmethod
    def _get_phone_from_image(cls, url: str) -> str:
        # pick house_id from url string
        house_id = url[-13:-5]
        screen_file = f"./data/phone/full_{house_id}.png"
        phone_img = cls._save_screenshot(screen_file, url)

        return cls._recognize_phone_image(screen_file, phone_img)

    @staticmethod
    def _save_screenshot(screen_file: str, url: str):
        driver = get_driver()
        driver.set_window_size(1366, 768)
        driver.get(url)
        driver.save_screenshot(screen_file)

        return driver.find_element_by_css_selector(".num img")

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
        return pytesseract.image_to_string(image)

    @staticmethod
    def _get_phone_from_text(html) -> str:
        return html.find(".num", first=True).text


class House:
    def __init__(self, url: str, title: str, html):
        self.url = url
        self.title = title
        self.phone = PhoneOperator.get_phone_from_url(url, html)

        self.lessor = html.find(".avatarRight i", first=True).text
        self.lessor_identity = html.find(".avatarRight", first=True).text.replace(
            self.lessor, ""
        )
        self.house_type, self.house_status = self._get_house_info(html)
        self.gender_requirement = self._get_gender_requirement(html)
        self.house_condition = html.find(".houseIntro", first=True).text

    @staticmethod
    def _get_house_info(html) -> Tuple:
        elements = html.find(".attr li")

        house_type = house_status = None
        for element in elements:
            if "型" in element.text:
                house_type = re.findall(r":\s*(.*)", element.text.replace("\n", ""))[0]
            elif "現" in element.text:
                house_status = re.findall(r":\s*(.*)", element.text.replace("\n", ""))[
                    0
                ]

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

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "lessor": self.lessor,
            "lessor_identity": self.lessor_identity,
            "house_type": self.house_type,
            "house_status": self.house_status,
            "phone": self.phone,
            "gender_requirement": self.gender_requirement,
            "house_condition": self.house_condition,
        }


def parse_single_house(url, title):
    r = HTMLSession().get(url)
    return House(url, title, r.html).to_dict()


def main():
    local_url_file = "data/urls_new.csv"
    basic_house_df = pd.read_csv(local_url_file)
    houses = basic_house_df.iloc[0:20].values.tolist()

    results = Parallel(n_jobs=-1)(
        delayed(parse_single_house)(houses[0], houses[1]) for houses in houses
    )

    logger.info(f"Parse {len(results)} Houses")
    logger.info(f"Sample: {results[0]}")

    full_house_df = pd.DataFrame.from_dict(results)
    full_house_df.to_csv("./data/info.csv", index=None)


if __name__ == "__main__":
    main()
