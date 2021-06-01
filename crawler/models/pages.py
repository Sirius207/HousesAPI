from typing import Any, Generator, Tuple
import csv
import time

from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


WAITING_TIME = 15


class HousePageOperator:
    def __init__(self, headless=True):
        self.driver = self.get_driver(headless)

    @staticmethod
    def get_driver(headless) -> webdriver.Chrome:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        )

        return webdriver.Chrome(options=chrome_options)

    def choose_city(self):
        city_btn = self.driver.find_element_by_css_selector("dd.pull-left")
        if city_btn.is_displayed():
            city_btn.click()

    def parse_house_url(self) -> Generator[Tuple[str, Any], None, None]:
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        urls = soup.select(".listLeft .infoContent h3 a")
        logger.info(f"Houses: {len(urls)}")
        return ((f"https:{url.get('href').strip()}", url.text.strip()) for url in urls)

    def click_next_page(self) -> bool:
        try:
            next_btn = WebDriverWait(self.driver, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pageNext"))
            )
            if next_btn.is_displayed():
                next_btn.click()
                return True

            logger.info("End of Pages")
            return False
        except StaleElementReferenceException:
            logger.warning("StaleElementReferenceException")
            return self.click_next_page()

    def get_current_page(self) -> str:
        try:
            page_btn = WebDriverWait(self.driver, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pageCurrent"))
            )
            logger.info(f"Change to Page {page_btn.text}")
            return page_btn.text
        except StaleElementReferenceException:
            logger.warning("StaleElementReferenceException")
            return self.get_current_page()

    @staticmethod
    def save_house_basic_info(writer, urls):
        writer.writerows(urls)
        logger.info("Write Success")

    def save_all_house_url(self, limit=3):
        url = "https://rent.591.com.tw/?kind=0&region=1"
        self.driver.get(url)
        self.choose_city()

        with open("data/urls.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)

            is_next_page = True
            new_page = 1
            while is_next_page and int(new_page) <= limit:
                time.sleep(2)
                new_page = self.get_current_page()

                urls = self.parse_house_url()
                self.save_house_basic_info(writer, urls)
                is_next_page = self.click_next_page()


if __name__ == "__main__":
    try:
        house_parser = HousePageOperator()
        house_parser.save_all_house_url()
    finally:
        logger.success("Quit Driver")
        house_parser.driver.quit()
