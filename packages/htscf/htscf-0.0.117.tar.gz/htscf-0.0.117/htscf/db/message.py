import time
from typing import Callable, Union
from pymongo import ASCENDING
from pymongo.collection import Collection
from htscf.utils.logging import Logger
import traceback

logger = Logger()


def send_message(collection, message, priority=1):
    document = {
        "message": message,
        "status": "new",
        "priority": priority,
        "createdAt": time.time()
    }
    collection.insert_one(document)


def listen_for_messages(collection: Collection, callback: Callable, delay: Union[int, float] = 1):
    try:
        while True:
            # 查找一个状态为 "new" 的消息，按创建时间排序
            message = collection.find_one_and_update(
                {"status": "new"},
                {"$set": {"status": "processing"}},
                sort=[("priority", ASCENDING), ("createdAt", ASCENDING)],
                return_document=True  # 确保返回更新后的文档
            )
            if message:
                try:
                    isProcessed = callback(message["message"])
                    if isProcessed:
                        collection.update_one({"_id": message["_id"]}, {"$set": {"status": "processed"}})
                    else:
                        collection.update_one({"_id": message["_id"]}, {"$set": {"status": "new"}})
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f"Error processing message {message['_id']}: {e}")
                    collection.update_one({"_id": message["_id"]}, {"$set": {"status": "error"}})
            else:
                # 没有新消息，短暂休眠
                time.sleep(delay)
    except KeyboardInterrupt:
        logger.info(f"Message Queue interrupt by user")
    except Exception as e:
        logger.error(f"Unexpected error occurred in message queue: {e}")
