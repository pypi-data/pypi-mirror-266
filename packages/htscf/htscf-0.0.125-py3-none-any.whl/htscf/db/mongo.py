from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection

# 处理不同优先级
IMMEDIATE = 1
NORMAL = 2
LOW = 3
IDLE = 4


def connect(dbName, collectionName, host="0.0.0.0", port=27017, ) -> Collection:
    client = MongoClient(host=host, port=port)
    db = client[dbName]
    return db[collectionName]


def log_message(message, level, log_db_name="log", log_collection_name="logs", db_host="0.0.0.0", db_port=27017):
    log_collection = connect(log_db_name, log_collection_name, db_host, db_port)
    log_entry = {
        'level': level,
        'message': message,
        'timestamp': datetime.now()
    }
    # 插入日志记录到集合
    log_collection.insert_one(log_entry)
