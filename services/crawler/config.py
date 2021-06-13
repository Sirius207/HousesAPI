import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    city_id = int(os.environ.get("CITY_ID", 1))
    urls_file = os.environ.get("URL_OUTPUT", f"data/urls_{city_id}.csv")
    data_file = os.environ.get("HOUSE_OUTPUT", f"data/temp_{city_id}.csv")
    page_limit = int(os.environ.get("PAGE_LIMIT", 3))
    url_start = int(os.environ.get("URL_START", 0))
    url_end = int(os.environ.get("URL_END", 250))
    executed_time = os.environ.get("EXECUTED_TIME", "02:13")
    use_docker = bool(int(os.environ.get("USE_DOCKER", 1)))

    chrome_host = os.environ.get("CHROME_HOST", "localhost")
