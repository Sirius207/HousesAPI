from typing import List
from argparse import ArgumentParser

from loguru import logger
from mongoengine import connect
from mongoengine.errors import BulkWriteError


from api.config import Config
from api.endpoints.houses.model import House
from api.loader.load_csv import get_houses


# pylint: disable= E1101
def save_data_to_mongo(houses_data: List[dict]):

    connect(
        db=Config.MONGODB_SETTINGS["db"],
        host=Config.MONGODB_SETTINGS["host"],
        username=Config.MONGODB_SETTINGS["username"],
        password=Config.MONGODB_SETTINGS["password"],
        port=27017,
    )

    houses = [House(**house_data) for house_data in houses_data]
    House.objects.insert(houses)


# pylint: enable= E1101

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="source file")
    args = parser.parse_args()

    try:
        save_data_to_mongo(get_houses(args.filename))
        logger.success("Save data to MongoDB Successfully")
    except BulkWriteError as error:
        logger.error(error)
