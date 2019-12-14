import pymongo

__all__ = ('get_mongodb_client', 'MongodbBase')

"""
all: 元素需要匹配条件所有值
size: 元素需要匹配组内元素数量
ne: 不等于
gt: 大于
gte: 大于或等于
lt: 小于
lte: 小于或等于
"""


def pop_key_from_dict(di):
    res = [k for k in di.keys()]
    return res[0] if len(res) == 1 else res


def process_commands(all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, **kwargs):
    commands = []
    if kwargs:
        commands.append(kwargs)
    if all:
        commands.append({key: {"$all": value} for key, value in all.items()})
    if size:
        commands.append({key: {"$size": value} for key, value in size.items()})
    if ne:
        commands.append({key: {"$ne": value} for key, value in ne.items()})
    if gt:
        commands.append({key: {"$gt": value} for key, value in gt.items()})
    if gte:
        commands.append({key: {"$gte": value} for key, value in gte.items()})
    if lt:
        commands.append({key: {"$lt": value} for key, value in lt.items()})
    if lte:
        commands.append({key: {"$lte": value} for key, value in lte.items()})
    query = {"$and": commands} if commands else {}
    return query


class MongodbClientCache:
    mongodb = None

    @classmethod
    def get_mongodb_client(cls, *args, **kwargs):
        if not cls.mongodb:
            cls.mongodb = pymongo.MongoClient(*args, **kwargs)
        return cls.mongodb


get_mongodb_client = MongodbClientCache.get_mongodb_client


class MongodbBase:
    def __init__(self, dbName, collName, **kwargs):
        self.dbName = dbName
        self.collName = collName
        self.client = get_mongodb_client(**kwargs)
        self.database = self.client[dbName]
        self.collection = self.database[collName]
        self._docs = self.collection.count()
        self._documents = None

    @property
    def documents(self):
        res, self._documents = self._documents, None
        return res

    @property
    def docs(self):
        res, self._docs = self._docs, None
        return res

    def _count(self):
        self._docs = self.collection.count()

    def count(self, all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, **kwargs):
        """
        mongodb.count(all={'commit_count': [3]}).docs -> {'commit_count': [1, 2, 3]}
        """
        query = process_commands(all, size, ne, gt, gte, lt, lte, **kwargs)
        self._docs = self.collection.count(query)
        return self

    def filter(self, all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, **kwargs):
        return self.count(all, size, ne, gt, gte, lt, lte, **kwargs).docs != 0

    def find(self, all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, **kwargs):
        query = process_commands(all, size, ne, gt, gte, lt, lte, **kwargs)
        self._documents = self.collection.find_one(query)
        return self

    def findAll(self, all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, field=None, **kwargs):
        query = process_commands(all, size, ne, gt, gte, lt, lte, **kwargs)
        self._documents = [doc[pop_key_from_dict(field)] if field and len(field) == 1 else doc for doc in
                           self.collection.find(query, field)]
        if field and len(field) != 1:
            self._documents = [[d for d in doc.values()] for doc in self._documents]
        return self

    def pop(self, all=None, size=None, ne=None, gt=None, gte=None, lt=None, lte=None, **kwargs):
        query = process_commands(all, size, ne, gt, gte, lt, lte, **kwargs)
        self._documents = self.collection.find_one_and_delete(query)
        self._count()
        return self

    def update(self, set=None, unset=None, upsert=False, **kwargs):
        """
        mongodb.update(commit_count=3, set={'commit_month': 123789})
        mongodb.update(commit_count=3, set={'commit_month': 123789, 'commit_count': 5})
        """
        command = dict()
        if set:
            command = {"$set": set}
        elif unset:
            command = {"$unset": set}
        self.collection.update_one(kwargs, command, upsert=upsert)
        self._count()
        return self

    def updateAll(self, set=None, unset=None, upsert=False, **kwargs):
        command = dict()
        if set:
            command = {"$set": set}
        elif unset:
            command = {"$unset": set}
        self.collection.update_many(kwargs or {}, command, upsert=upsert)
        self._count()
        return self

    def insert(self, new_document=None, **kwargs):
        """
        mongodb.insert({'commit_month': 123123, 'commit_count': [1,2,3,4]})
        :param new_document:
        :param kwargs:
        :return:
        """
        self.collection.insert_one(new_document or kwargs)
        self._count()
        return self

    def insertAll(self, new_documents_list: list):  # insert_many(list)
        self.collection.insert_many(new_documents_list)
        self._count()
        return self

    def removeAll(self, **kwargs):
        self.collection.delete_many(kwargs)
        self._count()
        return self

    def drop(self, name=None):
        name = name if name else self.collName
        self.database.drop_collection(name)
        return self
