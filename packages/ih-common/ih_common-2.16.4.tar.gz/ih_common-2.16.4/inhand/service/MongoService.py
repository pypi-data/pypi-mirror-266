#encoding=utf-8
import traceback

from pymongo import MongoClient

import logging
operators=['gt','lt','gte','lte','eq','ne','exist','regex','options','not','nor','or','and','in','nin','all','elemMatch','within','near','nearSphere']

class MongoDBService:

    @staticmethod
    def getInstance(settings):
        client = MongoClient(host=settings.host,
                             port=settings.port,
                             username=settings.username,
                             password=settings.password,
                             maxPoolSize = settings.maxPoolSize,
                             waitQueueMultiple=settings.waitQueueMultiple)
        #db_auth =client.admin
        #db_auth.authenticate(settings.account,settings.password)
        return client

    def __init__(self,db,mongoclient:MongoClient):
        self.db = db
        self.mongoclient = mongoclient
        self.conn = None #mongoclient.pool


    def __connect(self):
        if self.conn is None:
            #self.conn = MongoClient(self.settings.host,self.settings.port)
            #db_auth = self.conn.admin
            #db_auth.authenticate(self.settings.account,self.settings.password)
            self.conn = self.mongoclient


    def __close(self):
        if self.conn != None:
            try:
                #self.conn.close()
                pass
            finally:
                self.conn = None
                logging.info('Close the connnection with mongodb.')

    def close(self):
        self.__close()

    #向${collection}表新增一条记录${data}
    def insert_one(self,collection,data):
        if data is None:
            return
        self.__connect()
        db=self.conn[self.db]
        tbl=db[collection]
        x = tbl.insert_one(data)
        logging.debug("New a record into {}: {}".format(collection,data))
        self.close()
        return x.inserted_id

    # 向${collection}表新增一条记录${data}
    def insert_many(self, collection, data):
        if data is None:
            return
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        x = tbl.insert_many(data)
        cnt=len(x.inserted_ids)
        self.close()
        logging.debug("New {} records into {}".format(cnt,collection))
        return cnt




    #根据${query}查找一条记录
    def find_one(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]

        filter=self.__toMongoOperator(query)
        ret = tbl.find_one(filter)

        self.close()
        return ret

    #根据${query}查找多条记录 query: {field: ${filed_filter}},sort: [{field: ${1 | -1}}]
    def find(self,collection,query,sort,page_no,page_size,fields=None):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        limit = 0 if page_size is None or page_size <= 0 else page_size
        skip = 0 if page_size is None or page_size <= 0 else (page_no-1)*page_size
        pn = 1 if page_size is None or page_size <= 0 else page_no
        result = None
        if sort is None or len(sort) ==0:
            sort=[('_id', -1)]
        if fields is not None and len(fields) > 0:
            fieldMap = {}

            for field in fields:
                fieldMap[field] = 1
            #result= tbl.find(filter=filter, limit=limit, skip=skip, sort=sort,fields=fieldMap)
            result=tbl.find(filter,fieldMap).sort(sort).skip(skip).limit(limit)
        else:
            #result= tbl.find(filter=filter, limit=limit, skip=skip, sort=sort)
            result=tbl.find(filter).sort(sort).skip(skip).limit(limit)
        total=tbl.count_documents(filter=filter) #.find(filter=filter).count()

        self.close()
        return {'total':total,'page_no': pn,'cursor': skip,'limit': limit, 'result':list(result)}

    """
    根据filte计算符合的记录条数
    """
    def count(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        cnt = tbl.count_documents(filter=filter)#find(filter=filter).count()
        self.close()
        return cnt

    """
        更新最先匹配filter的一行记录
        update: {${field}:${value}}
        """

    def upsert(self, collection, query, update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter = self.__toMongoOperator(query)
        result = tbl.update_one(filter, {'$set': update},upsert=True)
        cnt= result.matched_countind(filter=filter).count()
        self.close()
        return cnt
    """
    更新最先匹配filter的一行记录
    update: {${field}:${value}}
    """
    def update_one(self,collection,query,update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result = tbl.update_one(filter,{'$set':update})
        self.close()
        return result.matched_count
    """
    更新最先匹配filter的所有记录
    update: {${field}:${value}}
    """
    def update_many(self,collection,query,update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result= tbl.update_many(filter,{'$set':update})
        self.close()
        return result.matched_count

    def delete(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result= tbl.remove(filter,update)
        self.close()
        return result['ok']



    def __fromMathOprator(self,operator):
        if operator=='>':
            return 'gt'
        elif operator == '>=':
            return 'gte'
        elif operator=='<':
            return 'lt'
        elif operator == '<=':
            return 'lte'
        elif operator=='==':
            return 'eq'
        elif operator == '!=':
            return 'ne'
        else:
            return operator


    def __toMongoOperator(self,filters):
        query={}
        for key in filters.keys():
            newKey=self.__fromMathOprator(key)
            if newKey in operators:
                newKey = '$'+key
            v=filters[key]
            if isinstance(v,dict):
                query[newKey]=self.__toMongoOperator(v)
            elif isinstance(v,list):
                vs = []
                for item in v:
                    if isinstance(item,dict):
                        vs.append(self.__toMongoOperator(item))
                    else:
                        vs.append(item)

                query[newKey]=vs
            else:
                query[newKey]=v

        return query

if __name__ == '__main__':
    mongoclient =MongoClient(host="mongodb",
                             port=27017,
                             username="root",
                             password="1qaz2wsx",
                             maxPoolSize=50, waitQueueMultiple=10)

    #mongoclient =MongoClient("mongodb",27017,maxPoolSize=50, waitQueueMultiple=10)
    #db_auth = mongoclient.admin
    #db_auth.authenticate("root","1qaz2wsx")

    mongo =MongoDBService("poweris",mongoclient)
    ret = mongo.find("clients",{"app_id":{"$eq":"hr"}},[('id',-1)],1,10)
    print(ret)
    mongo.mongoclient.close()
    ret = mongo.find("biz.logs",{},[('id',-1)],1,10)
    print(ret)







