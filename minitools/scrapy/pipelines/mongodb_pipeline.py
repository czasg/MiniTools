from logging import WARNING
from scrapy.item import BaseItem
from scrapy.exceptions import NotConfigured, DropItem
from minitools.db.mongodb import get_mongodb_client

__all__ = "MONGODB_PIPELINE",

# this pipeline just do one thing, which is insert one dict into mongodb.
MONGODB_PIPELINE = {
    "ITEM_PIPELINES": {
        "minitools.scrapy.pipelines.mongodb_pipeline.MongodbPipeline": 300,
    },
    "mongodb_db": "minitools",
    "mongodb_coll": "minitools",
    "mongodb_config": {},
}


class MongodbPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        mongodb_db = crawler.settings.get("mongodb_db", None)
        mongodb_coll = crawler.settings.get("mongodb_coll", None)
        if not all((mongodb_db, mongodb_coll)):
            crawler.spider.log("Mongodb can't loaded without attribute `mongodb_db`/`mongodb_coll`", level=WARNING)
            raise NotConfigured
        kwargs = crawler.settings.getdict("mongodb_config", {})
        return cls(crawler, mongodb_db, mongodb_coll, **kwargs)

    def __init__(self, crawler, mongodb_db, mongodb_coll, **kwargs):
        self.not_log_detail = crawler.settings.getbool("mongodb_not_log_detail", True)
        self.mongodb_client = get_mongodb_client(**kwargs)
        self.mongodb = self.mongodb_client[mongodb_db][mongodb_coll]

    def process_item(self, item, spider):
        try:
            into_mongodb = False
            if isinstance(item, (dict, BaseItem)):
                self.mongodb.insert_one(dict(item))
                into_mongodb = True
        except:
            raise DropItem
        else:
            if into_mongodb and self.not_log_detail:
                item = {"MongodbPipeline": "save success!"}
            return item
