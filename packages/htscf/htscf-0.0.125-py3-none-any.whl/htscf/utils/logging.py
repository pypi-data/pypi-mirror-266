"""
This package is designed for logging purposes and enables the seamless uploading of log entries to a MongoDB database.
"""
from functools import partial
from typing import Protocol, Any

from htscf.db.mongo import log_message
from htscf.utils.constants import LOG_DB_CONSTANTS, LOG_LEVEL_CONSTANTS


class ILogger(Protocol):
    def log(self, message: Any, level: int = LOG_LEVEL_CONSTANTS.LOG_LEVEL_INFO) -> None:
        ...

    def __call__(self, message: Any, level: int = LOG_LEVEL_CONSTANTS.LOG_LEVEL_INFO) -> None:
        ...


class __Logger:
    def __init__(self,
                 log_db_name: str,
                 log_collection_name: str,
                 db_host: str,
                 db_port: int):
        self.log_db_name = log_db_name or LOG_DB_CONSTANTS.LOG_DB_NAME
        self.log_collection_name = log_collection_name or LOG_DB_CONSTANTS.LOG_COLLECTION_NAME
        self.db_host = db_host or LOG_DB_CONSTANTS.LOG_DB_HOST
        self.db_port = db_port or LOG_DB_CONSTANTS.LOG_DB_PORT
        self.logger_func = partial(log_message, log_db_name=self.log_db_name, log_collection_name=self.log_collection_name, db_host=self.db_host, db_port=self.db_port)

    def log(self, message: Any, level: int = LOG_LEVEL_CONSTANTS.LOG_LEVEL_INFO) -> None:
        self.logger_func(message=message, level=level)

    def __call__(self, message: Any, level: int = LOG_LEVEL_CONSTANTS.LOG_LEVEL_INFO) -> None:
        self.log(message, level)


def _create_logger(log_db_name: str = None, log_collection_name: str = None, db_host: str = None, db_port: int = None) -> ILogger:
    return __Logger(log_db_name, log_collection_name, db_host, db_port)


class Logger:
    def __init__(self, log_db_name: str = None, log_collection_name: str = None, db_host: str = None, db_port: int = None):
        self._logger = _create_logger(log_db_name, log_collection_name, db_host, db_port)

    def emergency(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_EMERGENCY)

    def alert(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_ALERT)

    def critical(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_CRITICAL)

    def error(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_ERROR)

    def warning(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_WARNING)

    def notice(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_NOTICE)

    def info(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_INFO)

    def debug(self, message):
        self._logger(message, LOG_LEVEL_CONSTANTS.LOG_LEVEL_DEBUG)
