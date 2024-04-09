# -*- coding:UTF-8 -*-
import math
import os
import sys
import psutil
import warnings

import pandas as pd
import pymongo
import requests


def in_severs() -> bool :
    loc: str=os.getenv('SERVER_LOCATION')
    if (loc=='CN' or loc is None) and sys.platform.startswith('linux') :
        return True
    else :
        return False


def get_mongodb() :
    return os.environ.get('MONGODB_URL')


def get_db_info(db: object) -> object :
    db_evn=get_mongodb()
    bank_client=pymongo.MongoClient(db_evn)
    bank_col=bank_client['db-info']['raw_db']
    db_info=bank_col.find_one({'_id' : db})
    if not db_info :
        db_info=bank_col.find_one({'_id' : '_key_'})
        db_info['db']=db
        del db_info['_id']
    return db_info


def df_creator(data, index=None, delitem=None) :
    if delitem is None :
        delitem=[]
    if index :
        df=pd.DataFrame(data, index=index)
    else :
        df=pd.DataFrame(data)
    for i in delitem :
        del df[i]
    return df


def _dblink() :
    db_evn=get_mongodb()
    bank_client=pymongo.MongoClient(db_evn)
    bank_col=bank_client['db-info']['raw_db']
    return bank_col


def dblink(db, col) :
    db_info=_dblink().find_one({'_id' : db})
    client=pymongo.MongoClient(db_info['uri'])
    db=client[db_info['db']]
    collection=db[col]
    return collection


def col_stats(db, col) :
    db_info=_dblink().find_one({'_id' : db})
    client=pymongo.MongoClient(db_info['uri'])
    db=client[db_info['db']]
    return db.command('collstats', col)


def db_stats(db) :
    db_info=_dblink().find_one({'_id' : db})
    client=pymongo.MongoClient(db_info['uri'])
    db=client[db_info['db']]
    return db.command('dbstats')


def dblink_help(db=False) :
    if db :
        db_info=_dblink().find_one({'_id' : db})
        client=pymongo.MongoClient(db_info['uri'])
        db=client[db_info['db']]
        return db.collection_names()
    else :
        dbs=_dblink().find()
        return [i['_id'] for i in dbs]


def df2mongo(df, col) :
    data=df.to_dict('records')
    col.insert_many(data)


def mongo2df(col, match=None, projection=None, sort=None, skip=0, limit=0) :
    return df_creator(list(col.find(filter=match, projection=projection, sort=sort, skip=skip, limit=limit)))


def collection_show(db, col) :
    return mongo2df(dblink(db, col), limit=100)


def dblink_add(_id, uri, db=False) :
    _dblink().insert({'_id' : _id, 'uri' : uri, 'db' : db if db is not False else uri.split('/')[-1]})
    return _id in dblink_help()


def dblink_remove(_id) :
    _dblink().remove({'_id' : _id})


def dblink_update(_id, uri, db=False) :
    _dblink().update({'_id' : _id}, {'uri' : uri, 'db' : db if db is not False else uri.split('/')[-1]})


def get_token(job, on) :
    db_evn=get_mongodb()
    bank_client=pymongo.MongoClient(db_evn)
    bank_col=bank_client['tk'][job]
    tk=bank_col.find_one({'on' : on})
    return tk['token'], tk['servers']


def crawler_starter(db: str, col: str, work_on: str) :
    db=get_db_info(db)['db']
    token, servers=get_token('crawler_starter', work_on.upper())
    body={"db" : db, "table" : col, "token" : token}
    return requests.post(url=servers, json=body)
