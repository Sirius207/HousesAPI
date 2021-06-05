import pandas as pd
from loguru import logger
from mongoengine import connect

from config import Config
from endpoints.houses.model import House

connect(
    db=Config.MONGODB_SETTINGS["db"],
    host=Config.MONGODB_SETTINGS["host"],
    username=Config.MONGODB_SETTINGS["username"],
    password=Config.MONGODB_SETTINGS["password"],
    port=27017,
)


df = pd.read_csv("data/temp_info.csv")

df["house_id"] = df["url"].map(
    lambda url: url.replace("https://rent.591.com.tw/rent-detail-", "")[:-5]
)
df = df.drop(["url"], axis=1)

unique_df = df.drop_duplicates()
logger.info(f"Origin: {len(df)}, Drop Duplicates: {len(unique_df)}")

houses = [House(**house_data) for house_data in unique_df.to_dict("records")]
House.objects.insert(houses)
