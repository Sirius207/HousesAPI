from argparse import ArgumentParser

from loguru import logger
from mongoengine import connect
from mongoengine.errors import BulkWriteError
from pymongo import UpdateOne

from api.config import Config
from api.endpoints.houses.model import House
from api.loader.load_csv import get_houses


# pylint: disable= E1101
def save_data_to_mongo(filename: str):
    """use bulkwrite to import house data to mongoDB

    Args:
        filename (str): the filename of house data
    """

    houses_data = get_houses(filename)

    connect(
        db=Config.MONGODB_SETTINGS["db"],
        host=Config.MONGODB_SETTINGS["host"],
        username=Config.MONGODB_SETTINGS["username"],
        password=Config.MONGODB_SETTINGS["password"],
        port=27017,
    )

    houses = [House(**house_data) for house_data in houses_data]

    bulk_operations = [
        UpdateOne(
            {"_id": house.house_id}, {"$set": house.to_mongo().to_dict()}, upsert=True
        )
        for house in houses
    ]

    House._get_collection().bulk_write(bulk_operations, ordered=False)

    logger.success("Save data to MongoDB Successfully")


# pylint: enable= E1101

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="source file")
    args = parser.parse_args()

    try:
        save_data_to_mongo(args.filename)
    except BulkWriteError as error:
        logger.error(error)
