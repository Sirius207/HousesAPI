from argparse import ArgumentParser
from typing import List

import pandas as pd
from joblib import Parallel, delayed
from loguru import logger

from crawler.models.houses import parse_single_house
from crawler.models.pages import parse_houses_url


def _load_basic_houses_info(
    local_url_file: str = "data/urls.csv", start: int = 0, end: int = 2
) -> List[List[str]]:
    """load url and title of houses data

    Returns:
        List: e.g. [["https://..", "title_a"], ...]
    """
    # load url sources
    basic_house_df = pd.read_csv(local_url_file)
    return basic_house_df.iloc[start:end].values.tolist()


def _parallel_parse_house_data(basic_houses_info: List[List[str]]) -> List[dict]:
    """parse house data from all the urls with multiprocess mode (loki)

    Args:
        basic_houses_info (List[List[str]]): [("https://..", "house title"), ...]

    Returns:
        List[dict]: [{"url": "", "house_type": "",...}, ...]
    """
    houses = Parallel(n_jobs=-1)(
        delayed(parse_single_house)(house_info[0], house_info[1])
        for house_info in basic_houses_info
    )
    # filter deleted houses
    return [house for house in houses if house]


def _export_house_data_to_csv(output_file: str, houses: dict):
    full_house_df = pd.DataFrame.from_dict(houses)
    full_house_df.to_csv(output_file, index=None)


def main(args):
    parse_houses_url(args.urls_file, city_id=args.city_id)
    basic_houses_info = _load_basic_houses_info(
        args.urls_file, args.url_start, args.url_end
    )
    houses = _parallel_parse_house_data(basic_houses_info)

    logger.info(f"Parse {len(houses)} Houses")
    logger.info(f"Sample: {houses[0]}")

    _export_house_data_to_csv(args.data_file, houses)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--urls_file",
        dest="urls_file",
        help="file for urls storage",
        default="data/urls.csv",
    )
    parser.add_argument(
        "--data_file",
        dest="data_file",
        help="file for house data storage",
        default="data/temp_info.csv",
    )
    parser.add_argument(
        "--city_id", dest="city_id", help="city_id for parsing", default=1
    )
    parser.add_argument(
        "--url_start",
        dest="url_start",
        help="the start index for house parsing",
        default=0,
    )
    parser.add_argument(
        "--url_end", dest="url_end", help="the end index for house parsing", default=250
    )
    cli_args = parser.parse_args()

    main(cli_args)
