import json
import os
from typing import List
from argparse import ArgumentParser
from ssl import create_default_context, CERT_REQUIRED

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from loguru import logger

from api.loader.load_csv import get_houses


load_dotenv()


class ESConfig:
    host = os.environ.get("ES_HOST", "localhost")
    port = int(os.environ.get("ES_PORT", 9200))
    index = os.environ.get("ES_INDEX", "houses-data")
    username = os.environ.get("ES_USER")
    password = os.environ.get("ES_PASSWORD")


class ESOperator:
    def __init__(self, Config):
        context = create_default_context(cafile="data/es01.crt")
        context.load_verify_locations(cafile="data/ca.crt")
        context.verify_mode = CERT_REQUIRED
        self.es_conn = Elasticsearch(
            hosts=[Config.host],
            port=Config.port,
            http_auth=(Config.username, Config.password),
            scheme="https",
            ssl_context=context,
        )
        self.index = Config.index

    def create_index(self, index: str):

        is_index_exist = self.es_conn.indices.exists(index=index)
        if not is_index_exist:
            body = dict()
            body["settings"] = self._get_setting()
            body["mappings"] = self._get_mappings()
            logger.info(json.dumps(body))
            self.es_conn.indices.create(index=index, body=body)

            is_index_exist = self.es_conn.indices.exists(index=index)

        logger.success(self.es_conn.indices.get(index=index))
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
            self.es_conn.index(index=self.index, body=record, id=record["house_id"])

    def bulk_save(self, data: List[dict]):
        insert_data = [
            {
                "_op_type": "index",
                "_index": self.index,
                "_id": record["house_id"],
                "_source": record,
            }
            for record in data
        ]
        helpers.bulk(self.es_conn, insert_data)

    def bulk_delete(self, data: List[dict]):
        remove_data = [
            {"_op_type": "index", "_index": self.index, "_id": record["house_id"]}
            for record in data
        ]
        helpers.bulk(self.es_conn, remove_data)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="source file")
    args = parser.parse_args()

    es = ESOperator(ESConfig)
    es.create_index(ESConfig.index)

    houses = get_houses(args.filename)
    es.load_data(houses)
    # es.bulk_save(houses)
    logger.success(f"success create {len(houses)} documents")
