from argparse import ArgumentParser

import pandas as pd
from loguru import logger
from mongoengine import connect

from api.config import Config
from api.endpoints.houses.model import House


def get_houses(filepath: str = "data/temp_info.csv"):
    df = pd.read_csv(filepath)

    df["house_id"] = df["url"].map(
        lambda url: url.replace("https://rent.591.com.tw/rent-detail-", "")[:-5]
    )
    df = df.drop(["url"], axis=1)

    unique_df = df.drop_duplicates()
    logger.info(f"Origin: {len(df)}, Drop Duplicates: {len(unique_df)}")

    return unique_df.to_dict("records")


def save_data_to_mongo(houses_data):

    connect(
        db=Config.MONGODB_SETTINGS["db"],
        host=Config.MONGODB_SETTINGS["host"],
        username=Config.MONGODB_SETTINGS["username"],
        password=Config.MONGODB_SETTINGS["password"],
        port=27017,
    )

    houses = [House(**house_data) for house_data in houses_data]
    House.objects.insert(houses)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="source file")
    args = parser.parse_args()

    houses_data = get_houses(args.filename)
    save_data_to_mongo(houses_data)
    logger.success("Save data to MongoDB Successfully")
