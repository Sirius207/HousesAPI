from typing import List
import json

import pandas as pd
from loguru import logger
from elasticsearch import Elasticsearch


def get_houses(filepath: str = "data/temp_info.csv") -> List[dict]:
    df = pd.read_csv(filepath)

    df["house_id"] = df["url"].map(
        lambda url: url.replace("https://rent.591.com.tw/rent-detail-", "")[:-5]
    )
    df = df.drop(["url"], axis=1)

    unique_df = df.drop_duplicates()
    logger.info(f"Origin: {len(df)}, Drop Duplicates: {len(unique_df)}")

    unique_df = unique_df.fillna("")

    return unique_df.to_dict("records")


class ESOperator:
    def __init__(self):
        self.es = Elasticsearch(hosts=["localhost"], port=9200)
        self.index = None

    def create_index(self, index: str = "houses-test"):

        is_index_exist = self.es.indices.exists(index=index)
        if not is_index_exist:
            body = dict()
            body["settings"] = self._get_setting()
            body["mappings"] = self._get_mappings()
            logger.info(json.dumps(body))
            self.es.indices.create(index=index, body=body)

            is_index_exist = self.es.indices.exists(index=index)

        logger.success(self.es.indices.get(index=index))
        logger.success(f"Index {index}: {is_index_exist}")
        self.index = index

    @staticmethod
    def _get_setting():
        settings = {"index": {"number_of_shards": 2, "number_of_replicas": 1}}

        return settings

    @staticmethod
    def _get_mappings():
        mappings = {
            "properties": {
                "house_id": {"type": "keyword"},
                "title": {"type": "text"},
                "city": {"type": "keyword"},
                "district": {"type": "keyword"},
                "lessor": {"type": "text"},
                "lessor_identity": {"type": "text"},
                "house_type": {"type": "keyword"},
                "house_status": {"type": "keyword"},
                "sold": {"type": "text"},
                "phone": {"type": "keyword"},
                "gender_requirement": {"type": "keyword"},
                "house_condition": {"type": "text"},
            }
        }

        return mappings

    def load_data(self, data: List[dict]):
        for record in data:
            self.es.index(index=self.index, body=record, id=record["house_id"])


if __name__ == "__main__":
    es = ESOperator()
    es.create_index()

    houses = get_houses()
    es.load_data(houses)
    logger.success(f"success create {len(houses)} documents")
