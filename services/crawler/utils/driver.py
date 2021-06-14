"""
Module for web driver activating
"""

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from crawler.config import Config


def get_driver(headless=True) -> webdriver.Chrome:
    """activate a web driver (chrome)

    Args:
        headless (bool): use headless mode or not

    Returns:
        webdriver.Chrome: web driver
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    )

    if Config.use_docker:
        logger.info("Enable Docker Selenium")
        return webdriver.Remote(
            command_executor=f"http://{Config.chrome_host}:4444/wd/hub",
            desired_capabilities=chrome_options.to_capabilities(),
        )

    return webdriver.Chrome(options=chrome_options)
