from mongoengine import connect
import pandas as pd

from endpoints.houses.model import House
from config import Config

connect(
    db=Config.MONGODB_SETTINGS["db"],
    host=Config.MONGODB_SETTINGS["host"],
    username=Config.MONGODB_SETTINGS["username"],
    password=Config.MONGODB_SETTINGS["password"],
    port=27017,
)


df = pd.read_csv("data/temp_info.csv")

houses = [House(**house_data) for house_data in df.to_dict("records")]
House.objects.insert(houses)
