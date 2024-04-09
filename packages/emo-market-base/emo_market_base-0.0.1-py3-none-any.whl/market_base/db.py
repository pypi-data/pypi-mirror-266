import logging
from typing import Any, Union
from cache_db.cache_db import CacheDB


class DB:

    def __init__(self, path: str) -> None:
        self.db = CacheDB(path)
        self.db.load_cache()

        self.logger = logging.getLogger("MarketBaseDB")

    def get(self, key: str, default: Union[Any, None] = None) -> Any:
        result = self.db.get(key, default)
        self.logger.info(f"Veri alındı. '{key}': '{result}'")
        return result

    def set(self, key: str, value, with_save: bool = True):
        self.db.cache[key] = value
        self.logger.info(f"Veri eklendi. '{key}': '{value}'")

        if with_save:
            self.db.save_cache()
            self.logger.info(f"Dosya kaydedildi: {self.db.file_path}")
