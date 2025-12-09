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
from bson import json_util
from pymongo import MongoClient
from omegaconf import DictConfig
from typing import Dict, Any, Union, Tuple, Sequence, Mapping, List

logger = logging.getLogger("inf.wrp.mongoDBSync")
DB_Sort = Sequence[Tuple[str, Union[int, str, Mapping[str, Any]]]]


class MongoDBWrapper:
    def __init__(self,
                 name: str = "MyDb",
                 collections: DictConfig = {},
                 host: str = "localhost",
                 port: int = 27017,
                 init_now: bool = True,
                 **kwargs):
        if init_now:
            self._host = host
            self._port = port
            self._db_name = name
            self._collections = collections
            self.connect()
            for c, c_inf in collections.items():
                self.create_collection(c_inf.name, c_inf.schema)

    def init(self,
             name: str,
             collections: DictConfig,
             host: str = "localhost",
             port: int = 27017,
             **kwargs):
        self._host = host
        self._port = port
        self._db_name = name
        self._collections = collections
        self.connect()
        for c, c_inf in collections.items():
            self.create_collection(c_inf.name, c_inf.schema)

    def close(self):
        self._client.close()
        logger.info(f"disconnect to {self._db_name}")

    def connect(self):
        self._client = MongoClient(self._host, self._port)
        self._db = self._client[self._db_name]
        logger.info(f"connect to {self._host}:{self._port} - {self._db_name}")

    def list_collections(self):
        return self._db.list_collection_names()

    def create_collection(self,
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
            # get validator
            list_pop = ["required", "unique", "expire"]
            for k in list_pop:
                if k in f_dict.keys():
                    f_dict.pop(k)

            validator['$jsonSchema']['properties'][field] = f_dict

        if len(required) > 0:
            validator['$jsonSchema']['required'] = required

        try:
            self._db.create_collection(collection_name)
            # Create index for unique
            for idx in index_data:
                logger.info(f"indexing info: {idx}")
                if idx.get("expire"):
                    self._db[collection_name].create_index(
                        idx.get("field"), unique=idx.get("unique", False), expireAfterSeconds=idx.get("expire")
                    )
                else:
                    self._db[collection_name].create_index(
                        idx.get("field"), unique=idx.get("unique", False)
                    )
            logger.info(f"Create collections {collection_name} success.")

            # validator
            self._db.command("collMod", collection_name, validator=validator)
        except Exception as e:
            logger.warning(e)

    def count(self, coll_name: str, query: Dict = {}, **kwargs):
        """
        query: {"first_name": "abc"}
        """
        res = 0
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            res = self._db[coll_name].count_documents(query)
        except Exception as e:
            logger.error(e)
        return res

    def insert(self, coll_name: str, document: Dict, **kwargs):
        res = None
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            res = self._db[coll_name].insert_one(document)
            res = res.inserted_id
            logger.debug(f"Insert to {coll_name} success")
        except Exception as ex:
            logger.error(ex)
        return res

    def query(self,
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
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if limit == 0:
                res = self._db[coll_name].find(query).sort(sort_by)
            else:
                res = self._db[coll_name].find(query).sort(sort_by).limit(limit)
            res = json_util.loads(json_util.dumps(res))
        except Exception as ex:
            logger.error(ex)
        return res

    def update(self, coll_name: str, query: Dict, new_value: Dict, mode="one", **kwargs):
        """
        example:
            query: {"first_name": "a0"}
            new_value:  {"first_name": "a000"}
        """
        res = -1
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if mode == "one":
                res = self._db[coll_name].update_one(query, {"$set": new_value})
            else:
                res = self._db[coll_name].update_many(query, {"$set": new_value})
            res = res.modified_count
        except Exception as ex:
            logger.error(ex)
        return res

    def delete(self, coll_name: str, query: Dict, mode="one", **kwargs):
        """
        example:
            query: {"first_name": "a0"}
            query: {"first_name": {"$regex": "^a"}}
        """
        res = -1
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        try:
            if mode == "one":
                res = self._db[coll_name].delete_one(query)
            else:
                res = self._db[coll_name].delete_many(query)
            res = res.deleted_count
        except Exception as e:
            logger.error(e)
        return res

    def aggregate(self, coll_name: str, pipeline: List[Dict]):
        assert coll_name in self.list_collections(), logger.error(f"{coll_name} invalid")
        res = []
        try:
            res = self._db[coll_name].aggregate(pipeline)
            res = json_util.loads(json_util.dumps(res))
        except Exception as ex:
            logger.error(ex)
        return res


# TEST CLASS
if __name__ == '__main__':
    """
    python3.10 inference/wrapper/mongoDBSync_wrapper.py
    """
    import os
    import sys

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, root_dir)
    sys.path.insert(0, os.path.join(root_dir, "inference"))

    from omegaconf import OmegaConf
    from hydra.utils import instantiate
    from hydra import compose, initialize

    logging.basicConfig(level=logging.DEBUG)

    initialize(config_path="../../cfg")
    cfg = compose(config_name="config")
    # print(OmegaConf.to_yaml(cfg))
    cfg = cfg.updateDb_api.database
    db = instantiate(cfg)

    version = db._client.server_info()["version"]

    print(version)
    # doc = {"username": "test", "password": "abc"}
    # r = db.insert("user", doc)
    # print(f"insert: {r}")
    camera_id = "908fb5494a3c443ea3739300dfc0c872"
    pipeline = [
        {"$match": {"camera_id": camera_id}},
        {"$sort": {"_id": -1}},
        {"$limit": 1},
        {"$lookup": {
            "from": "cameras",
            "localField": "camera_id",
            "foreignField": "camera_id",
            "as": "camera_info",
            }
         },
        {"$set": {
            "visualize": {"$first": "$camera_info.visualize"},
            "regions": {"$first": "$camera_info.regions"},
        }},
        {"$project": {"camera_info": 0}}
    ]
    _res = db.aggregate("frames", pipeline=pipeline)
    print(_res)

