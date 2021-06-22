import os
from typing import List

import pandas as pd
from loguru import logger


def get_houses(filepath: str = "data/temp_info.csv") -> List[dict]:
    """read houses data, create house_id column, drop duplicated data

    Args:
        filepath (str, optional): the path of house data. Defaults to "data/temp_info.csv".

    Returns:
        List[dict]: [{"house_id": "", "house_type: "", ...}, ...]
    """
    house_df = pd.read_csv(filepath)

    house_df["house_id"] = house_df["url"].map(
        lambda url: url.replace(os.environ.get("WEB_URL_PREFIX"), "")[:-5]
    )
    house_df = house_df.drop(["url"], axis=1)

    unique_df = house_df.drop_duplicates(subset=["house_id"])
    logger.info(f"Origin: {len(house_df)}, Drop Duplicates: {len(unique_df)}")

    unique_df = unique_df.fillna("")

    return unique_df.to_dict("records")
