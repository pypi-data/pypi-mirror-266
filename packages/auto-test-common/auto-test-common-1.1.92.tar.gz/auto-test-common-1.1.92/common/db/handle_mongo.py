from pymongo import MongoClient
from common.common.constant import Constant
from common.common.api_driver import APIDriver

class MongoDB():

    my_db = None

    def __init__(self, config):
        """初始化连接MongoDb"""
        my_client = MongoClient(config.get("host"), config.get("port"))
        self.my_db = my_client[config.get("dbName")]
        if config.get("dbUsername") is not None:
            self.my_db.authenticate(config.get("dbUsername"), config.get("dbPasswd"))

    @classmethod
    def mongo_db(self, _key, env: str = Constant.ENV):
        """
        返回MongoDB数据库
        """
        config = MongoDB.get_db_config(_key, env)
        return MongoDB(config)

    @classmethod
    def mongo_collection(self, _key, _collection, env: str = Constant.ENV):
        """
            返回MongoDB集合
        """
        my_db = MongoDB.mongo_db(_key, env)
        my_col = my_db[_collectin]
        return my_col

    @classmethod
    def mongo_find(self, _key, _collection, _query, type: str = "", limit: int = 0, _sort: str = "",
                   env: str = Constant.ENV):
        """
        查询集合中数据
        """
        my_db = MongoDB.mongo_db(_key, env)
        my_col = my_db[_collectin]
        if DataProcess.isNotNull(_query):
            if type.find("{}") >= 0:
                datas = my_col.find({}, query)
            else:
                datas = my_col.find(query)
        else:
            datas = my_col.find()
        if limit != 0:
            datas.limit(limit)
        if type.find("ASC") >= 0:
            datas.sort(_sort, -1)
        if type.find("DESC") >= 0:
            datas.sort(_sort, 1)
        return datas

    @classmethod
    def get_db_config(self, db_key, db_env):
        _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/getDBConfig/{db_key}/{db_env}",
                                           method='get'
                                           )
        return _tempdata.json()