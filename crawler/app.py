from typing import List

import pandas as pd
from joblib import Parallel, delayed
from loguru import logger

from crawler.models.houses import parse_single_house


def _load_basic_houses_info(start: int = 0, end: int = 2) -> List[List[str]]:
    """load url and title of houses data

    Returns:
        List: e.g. [["https://..", "title_a"], ...]
    """
    # load url sources
    local_url_file = "data/urls_new.csv"
    basic_house_df = pd.read_csv(local_url_file)
    return basic_house_df.iloc[start:end].values.tolist()


def _parallel_parse_house_data(basic_houses_info) -> List[dict]:
    houses = Parallel(n_jobs=-1)(
        delayed(parse_single_house)(house_info[0], house_info[1])
        for house_info in basic_houses_info
    )
    # filter deleted houses
    return [house for house in houses if house]


def _export_house_data_to_csv(houses: dict):
    full_house_df = pd.DataFrame.from_dict(houses)
    full_house_df.to_csv("./data/temp_info.csv", index=None)


def main():
    basic_houses_info = _load_basic_houses_info()
    houses = _parallel_parse_house_data(basic_houses_info)

    logger.info(f"Parse {len(houses)} Houses")
    logger.info(f"Sample: {houses[0]}")

    _export_house_data_to_csv(houses)


if __name__ == "__main__":
    main()
