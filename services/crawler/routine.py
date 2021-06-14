import time
from datetime import datetime

import schedule
from loguru import logger

from crawler.config import Config
from crawler.main import main


if __name__ == "__main__":

    schedule.every().day.at(Config.executed_time).do(main, args=Config)
    logger.info(
        f"Start Crawler: {Config.city_id}, {Config.executed_time}\n"
        f"{Config.urls_file}, {Config.data_file}\n"
        f"Page limit - {Config.page_limit}, Index - {Config.url_start}:{Config.url_end}\n"
        f"{datetime.now()}"
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
