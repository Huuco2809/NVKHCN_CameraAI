"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
mongodb wrapper
    insert
    find
    query
    delete
    update
"""
import os
import logging
import asyncio
from bson import json_util
from omegaconf import DictConfig
from inference.utils import utils
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, Union, Tuple, Sequence, Mapping, List

logger = logging.getLogger("inf.wrp.mongoDBAsync")
DB_Sort = Sequence[Tuple[str, Union[int, str, Mapping[str, Any]]]]


class MongoDBWrapper:
    def __init__(self, **kwargs):
        self._db = None
        self._uri = None
        self._db_name = None
        self._collections = None

    async def init(
            self,
            name: str = "MyDb",
            collections: DictConfig = {},
            host: str = "localhost",
            port: int = 27017, **kwargs
    ):
        self._db = None
        self._uri = f"mongodb://{host}:{port}"
        self._db_name = name
        self._collections = collections
        await self.connect()
        for c, c_inf in self._collections.items():
            await self.create_collection(c_inf.name, c_inf.schema)
        # return self

    async def close(self):
        self._client.close()
        logger.info(f"disconnect to {self._db_name}")

    async def connect(self):
        self._client = AsyncIOMotorClient(self._uri)
        self._db = self._client[self._db_name]
        logger.info(f"connect to {self._uri} - {self._db_name}")

    async def check_connect(self):
        """check and reconnect"""
        try:
            self._db.command("ping")
        except Exception as e:
            logger.warning(e)
            await self.connect()

    async def list_collections(self):
        return list(await self._db.list_collections())

    async def create_collection(
            self,
            collection_name: str,
            schema: DictConfig,
            **kwargs):
        validator = {'$jsonSchema': {'bsonType': 'object', 'properties': {}}}
        required = []
        index_data = []
        for field, f_dict in schema.items():
            f_dict = dict(f_dict)
            _index = {}
            # get list required and unique
            if f_dict.get("required"):
                required.append(field)
            if f_dict.get("unique"):
                _index["field"] = field
                _index["unique"] = True
            if f_dict.get("expire"):
                _index["field"] = field
                _index["expire"] = f_dict.get("expire")

            if _index:
                index_data.append(_index)

            # get validator
            list_pop = ["required", "unique", "expire"]
            for k in list_pop:
                if k in f_dict.keys():
                    f_dict.pop(k)
            validator['$jsonSchema']['properties'][field] = f_dict

        if len(required) > 0:
            validator['$jsonSchema']['required'] = required

        try:
            await self._db.create_collection(collection_name)
            # Create index
            for idx in index_data:
                logger.info(f"indexing info: {idx}")
                if idx.get("expire"):
                    await self._db[collection_name].create_index(
                        idx.get("field"), unique=idx.get("unique", False), expireAfterSeconds=idx.get("expire")
                    )
                else:
                    await self._db[collection_name].create_index(
                        idx.get("field"), unique=idx.get("unique", False)
                    )
            logger.info(f"Create collections {collection_name} success.")
            # validator
            await self._db.command("collMod", collection_name, validator=validator)

        except Exception as e:
            logger.warning(e)

    async def count(self, coll_name: str, query: Dict = {}, **kwargs):
        """
        query: {"first_name": "abc"}
        """
        res = 0
        # assert coll_name in await self.list_collections(), logger.error(f"{coll_name} invalid")
        # await self.connect()
        try:
            res = await self._db[coll_name].count_documents(query)
        except Exception as e:
            logger.error(f"Err: {e}")
        return res

    async def insert(self, coll_name: str, document: Dict, **kwargs):
        res = None
        await self.check_connect()
        try:
            res = await self._db[coll_name].insert_one(document)
            res = res.inserted_id
            logger.debug(f"Insert to {coll_name} success")

        except Exception as ex:
            logger.error(ex)
        return res

    async def query(
            self,
            coll_name: str, query: Dict,
            limit=0, sort_by: Union[str, DB_Sort] = "_id", **kwargs):
        """
        query example:
            {"first_name": "abc"} # get doc with first_name is "abc"
            {"first_name": {"$regex": "^a"}} # get doc with first_name include "a"
        example sort:
            sort_by="date_created"
            sort_by=[("date_created", -1)]
        check https://www.mongodb.com/docs/manual/meta/aggregation-quick-reference/#std-label-aggregation-expressions
        """
        res = []
        await self.check_connect()
        # assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if limit == 0:
                cursor = self._db[coll_name].find(query).sort(sort_by)
                res = await cursor.to_list(length=None)
            else:
                cursor = self._db[coll_name].find(query).sort(sort_by).limit(limit)
                res = await cursor.to_list(length=limit)

            res = json_util.loads(json_util.dumps(res))
        except Exception as ex:
            logger.error(ex)
        return res

    async def update(self, coll_name: str, query: Dict, new_value: Dict, mode="one", **kwargs):
        """
        example:
            query: {"first_name": "a0"}
            new_value:  {"first_name": "a000"}
        """
        await self.check_connect()
        res = -1
        # assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if mode == "one":
                res = await self._db[coll_name].update_one(query, {"$set": new_value})
            else:
                res = await self._db[coll_name].update_many(query, {"$set": new_value})
            res = res.modified_count
        except Exception as ex:
            logger.error(ex)
        return res

    async def delete(self, coll_name: str, query: Dict, mode="one", **kwargs):
        """
        example:
            query: {"first_name": "a0"}
            query: {"first_name": {"$regex": "^a"}}
        """
        await self.check_connect()
        res = -1
        # assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if mode == "one":
                res = await self._db[coll_name].delete_one(query)
            else:
                res = await self._db[coll_name].delete_many(query)
            res = res.deleted_count
        except Exception as e:
            logger.error(e)
        return res

    async def aggregate(self, coll_name: str, pipeline: List[Dict]):
        # assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        await self.check_connect()
        res = []
        try:
            cursor = self._db[coll_name].aggregate(pipeline)
            res = await cursor.to_list(length=None)
            res = json_util.loads(json_util.dumps(res))
        except Exception as ex:
            logger.error(ex)
        return res

    async def pagination(
            self,
            coll_name: str,
            page: int = 1,
            page_size: int = 10,
            sort: int = -1,
            match: Dict = None) -> List[Dict]:

        res = []
        try:
            if match is not None:
                cursor = self._db[coll_name].aggregate([{"$match": match}])
                res = await cursor.to_list(length=1)
                if len(res) == 0:
                    return []

            skip_size = page * page_size - page_size
            pipeline = [
                {"$sort": {"_id": sort}},  # 1 or -1
                {
                    "$facet": {
                        "metadata": [
                            {"$count": "total"},
                            {"$addFields": {"page": page}},
                            {"$addFields": {"page_size": page_size}}
                        ],
                        "items": [
                            {"$skip": skip_size},
                            {"$limit": page_size},
                            {"$project": {"_id": 0}},
                        ]
                    }
                },
                {
                    "$project": {
                        "total": {"$arrayElemAt": ["$metadata.total", 0]},
                        "pages": {
                            "$toInt": {"$ceil": {"$divide": [{"$arrayElemAt": ["$metadata.total", 0]}, page_size]}}},
                        "page": {"$arrayElemAt": ["$metadata.page", 0]},
                        "page_size": {"$arrayElemAt": ["$metadata.page_size", 0]},
                        "items": "$items",
                    }
                }
            ]

            if match is not None and isinstance(match, Dict):
                pipeline.insert(0, {"$match": match})
            cursor = self._db[coll_name].aggregate(pipeline)
            res = await cursor.to_list(length=None)
            res = json_util.loads(json_util.dumps(res))
        except Exception as ex:
            logger.error(ex)
        return res


# TEST CLASS
if __name__ == '__main__':
    """
    python3.10 inference/wrapper/mongoDBAsync_wrapper.py
    """
    import datetime
    from omegaconf import OmegaConf
    from hydra.utils import instantiate
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)

    initialize(config_path="../../cfg")
    cfg = compose(config_name="config")
    print(OmegaConf.to_yaml(cfg))
    cfg = cfg.updateDb_api.database
    db = MongoDBWrapper()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.init(**cfg))

    # doc = {"username": "test", "password": "abc"}
    # r = loop.run_until_complete((db.insert("user", doc)))
    # print(f"insert: {r}")
