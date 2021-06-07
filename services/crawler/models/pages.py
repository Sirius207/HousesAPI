import csv
import time
from typing import Any, Generator, Set, Tuple

from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WAITING_TIME = 15


class HousePageOperator:
    def __init__(self, headless: bool = True):
        self.driver = self.get_driver(headless)
        self.write_page: Set[str] = set()

    @staticmethod
    def get_driver(headless: bool) -> webdriver.Chrome:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        )

        return webdriver.Chrome(options=chrome_options)

    def choose_city(self, city_id: int = 1):
        city_btn = self.driver.find_element_by_css_selector(
            f'dd.pull-left[data-id="{city_id}"]'
        )
        logger.info(f"choose City: {city_btn.text}")
        if city_btn.is_displayed():
            city_btn.click()

    def parse_house_url(self) -> Generator[Tuple[str, Any], None, None]:
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        urls = soup.select(".listLeft .infoContent h3 a")
        logger.info(f"Houses: {len(urls)}")
        return ((f"https:{url.get('href').strip()}", url.text.strip()) for url in urls)

    def click_next_page(self, current_page: int) -> bool:
        try:
            next_btn = WebDriverWait(self.driver, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pageNext"))
            )
            if next_btn.is_displayed() and "last" not in next_btn.get_attribute(
                "class"
            ):
                next_btn.click()
                return True

            logger.info("End of Pages")
            return False
        except StaleElementReferenceException:
            new_page = self.get_current_page()
            if new_page == current_page:
                logger.warning(f"StaleElementReferenceException, Page: {new_page}")
                return self.click_next_page(current_page)

            return True

    def get_current_page(self) -> int:
        try:
            page_btn = WebDriverWait(self.driver, WAITING_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pageCurrent"))
            )
            logger.info(f"Change to Page {page_btn.text}")
            return int(page_btn.text)
        except StaleElementReferenceException:
            logger.warning("StaleElementReferenceException")
            return self.get_current_page()

    def save_house_basic_info(self, writer, urls, new_page):

        if new_page not in self.write_page:
            writer.writerows(urls)
            logger.info(f"Write Success {new_page}")
            self.write_page.add(new_page)

    def save_all_house_url(self, output_file, city_id: int = 1, page_limit: int = 3):
        # city_id: 3-新北, 1-台北
        url = "https://rent.591.com.tw/?kind=0&region=1&order=posttime&orderType=asc"
        self.driver.get(url)
        self.choose_city(city_id)

        with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            is_next_page = True
            new_page = 1
            last_page = 0
            while is_next_page and new_page <= page_limit:
                time.sleep(1)
                new_page = self.get_current_page()
                if last_page != new_page:
                    urls = self.parse_house_url()
                    self.save_house_basic_info(writer, urls, new_page)
                    last_page = new_page
                else:
                    logger.warning("the same page")
                is_next_page = self.click_next_page(new_page)


def parse_houses_url(output_file, city_id=1):
    try:
        house_parser = HousePageOperator()
        house_parser.save_all_house_url(
            output_file=output_file, city_id=city_id, page_limit=3
        )
    finally:
        logger.success("Quit Driver")
        house_parser.driver.quit()


if __name__ == "__main__":
    parse_houses_url("data/urls.csv")
