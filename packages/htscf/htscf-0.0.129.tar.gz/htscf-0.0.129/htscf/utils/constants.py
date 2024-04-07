# 处理不用日志类型
from os import getenv

__all__ = ["LOG_DB_CONSTANTS", "LOG_LEVEL_CONSTANTS"]


class LogLevelConstants:
    @property
    def LOG_LEVEL_EMERGENCY(self):
        return 1

    @property
    def LOG_LEVEL_ALERT(self):
        return 2

    @property
    def LOG_LEVEL_CRITICAL(self):
        return 3

    @property
    def LOG_LEVEL_ERROR(self):
        return 4

    @property
    def LOG_LEVEL_WARNING(self):
        return 5

    @property
    def LOG_LEVEL_NOTICE(self):
        return 6

    @property
    def LOG_LEVEL_INFO(self):
        return 7

    @property
    def LOG_LEVEL_DEBUG(self):
        return 8


class LogDbConstants:
    # 日志数据库配置
    @property
    def LOG_DB_NAME(self):
        return getenv("HTSCF_LOG_DB_NAME", "log")

    @property
    def LOG_COLLECTION_NAME(self):
        return getenv("HTSCF_LOG_COLLECTION_NAME", "logs")

    @property
    def LOG_DB_HOST(self):
        return getenv("HTSCF_LOG_DB_HOST", "0.0.0.0")

    @property
    def LOG_DB_PORT(self):
        try:
            return int(getenv("HTSCF_LOG_DB_PORT", 27017))
        except ValueError:
            return 27017

    @property
    def LOG_DB_NAME(self):
        return getenv("HTSCF_LOG_DB_NAME", "log")

    @property
    def LOG_DB_NAME(self):
        return getenv("HTSCF_LOG_DB_NAME", "log")


LOG_DB_CONSTANTS = LogDbConstants()
LOG_LEVEL_CONSTANTS = LogLevelConstants()
