import csv
from collections import defaultdict
import time
from typing import Any, List, Tuple

import pandas as pd
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
        self.write_page: dict = defaultdict(int)

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

    def parse_house_url(self) -> List[Tuple[str, Any]]:
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        urls = soup.select(".listLeft .infoContent h3 a")
        logger.info(f"Houses: {len(urls)}")
        return [(f"https:{url.get('href').strip()}", url.text.strip()) for url in urls]

    def click_prev_page(self):
        prev_btn = WebDriverWait(self.driver, WAITING_TIME).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagePrev"))
        )

        prev_btn.click()

    def click_next_page(self, current_page: int) -> bool:
        try:
            logger.info(f"Page: {current_page} -> click next page")
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

        if new_page not in self.write_page or self.write_page[new_page] < 2:
            writer.writerows(urls)
            logger.success(f"Write Success {new_page}")
            self.write_page[new_page] += 1

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
            last_tail_title = ""
            click_prev_page = False
            while is_next_page and new_page <= page_limit:
                time.sleep(1)
                new_page = self.get_current_page()
                if last_page != new_page:
                    urls = self.parse_house_url()
                    logger.info(f"Page Head:\n {urls[0][1]}")
                    logger.info(f"Page Tail:\n {urls[-1][1]}")
                    if (
                        urls[0][1] == last_tail_title
                        and self.write_page[new_page - 1] < 2
                    ):
                        # back to the page before prev
                        logger.warning(f"The Same House: {new_page}")
                        click_prev_page = True
                        self.click_prev_page()
                        time.sleep(1)
                        self.click_prev_page()
                        last_page = last_page - 2
                    else:
                        last_tail_title = urls[-1][1]
                        self.save_house_basic_info(writer, urls, new_page)
                        last_page = new_page
                elif last_page == new_page - 2:
                    logger.warning(f"Last Page: {last_page}, Current Page: {new_page}")
                    click_prev_page = True
                    self.click_prev_page()
                else:
                    logger.warning("The same page")

                if click_prev_page:
                    click_prev_page = False
                else:
                    is_next_page = self.click_next_page(new_page)


def parse_houses_url(output_file, city_id=3, page_limit=3):
    try:
        house_parser = HousePageOperator()
        house_parser.save_all_house_url(
            output_file=output_file, city_id=city_id, page_limit=page_limit
        )
        _remove_duplicate_houses(output_file)

    finally:
        logger.success("Quit Driver")
        house_parser.driver.quit()


def _remove_duplicate_houses(filepath):
    house_df = pd.read_csv(filepath)
    unique_df = house_df.drop_duplicates()
    logger.info(f"Origin: {len(house_df)}, Drop Duplicates: {len(unique_df)}")

    unique_df.to_csv("data/urls_unique.csv", index=None)


if __name__ == "__main__":
    parse_houses_url("data/urls.csv")
