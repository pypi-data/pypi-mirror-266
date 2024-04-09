# -*- coding:UTF-8 -*-
# ANBUtils/DBWorker.py
# Created by redbson on 2021-09-01
# Latest modified on 2023-03-28

# This module provides a MongoDB database worker class for data operations. The class provides methods for connecting
# to a MongoDB database, retrieving data from collections, and inserting data into collections. The class also
# provides methods for auditing collections and the database. The class can be used to perform various data
# operations on MongoDB databases.


import hashlib
import math
import os
import psutil
import time
import warnings
from typing import List, Dict, Callable
from .db_tools import in_severs, get_mongodb, get_db_info, df_creator
import pymongo
import pandas as pd


class DBWorker(object):
    def __init__(self, db):
        """
        Initialize a MongoDB database worker.

        Args:
            db (str): The name of the database.
        """
        db_info: dict = get_db_info(db)
        public_uri: str = os.environ.get('MONGODB_PUB_URI')
        uri: str = db_info['uri'] if in_severs() else (db_info['uri'].split(
            '@')[0] + '@' + public_uri + ':' + db_info['uri'].split(':')[-1])
        self.db_code: str = db
        self.client: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.db: pymongo.database.Database = self.client[db_info['db']]
        self.col: List[Dict[str, pymongo.collection.Collection]] = {}
        self._link('__audit__')
        self._link('__log__')

    def _link(self, col: str) -> None:
        if col not in self.col:
            self.col[col] = self.db[col]

    def link(self, col: str) -> pymongo.collection.Collection:
        """
        Get a reference to the specified collection in the database.

        Args:
            col (str): The name of the collection.

        Returns:
            pymongo.collection.Collection: The collection object.
        """
        self._link(col)
        return self.col[col]

    def _last_audit(self, col_name) -> dict or None:
        return self.link('__audit__').find_one(
            {"collection": col_name}, sort = [("audit_ts", -1)])

    def _audit(self, col_name: str) -> bool:
        def quick_audit_col(_col_name: str, _factor: str = '') -> dict:
            _version: str = '0.0.1'
            time_stamp: int = time.time_ns()
            stats: dict = self.get_col_stats(col_name)
            stream: str = (
                f"{stats['ns']}:{stats['size']}#{stats['count']}#{stats['size']}#{stats['storageSize']}#"
                f"{stats['nindexes']}#{stats['totalIndexSize']}")
            hash_result: str = hashlib.sha256(
                stream.encode('utf-8')).hexdigest()
            _id: str = hashlib.sha256(
                f"{hash_result}:{time_stamp}@{factor}".encode('utf-8')).hexdigest()
            return {
                "_id": _id,
                "collection": col_name,
                "ns": stats['ns'],
                "hash": hash_result,
                "document_count": stats['count'],
                "data_size": stats['size'],
                "storage_size": stats['storageSize'],
                "index_count": stats['nindexes'],
                "total_index_size": stats['totalIndexSize'],
                "average_object_size": stats['avgObjSize'] if 'avgObjSize' in stats else 'N/A',
                "raw_data": stats,
                "audit_time_stamp": time_stamp,
                "meta": {
                    "method": "quick_audit_collection",
                    "version": _version}}

        last_report: dict or None = self._last_audit(col_name)
        factor: str = last_report['hash'] if last_report is not None else ''
        new_report: dict = quick_audit_col(col_name, factor)

        if last_report is None:
            self.link('__audit__').insert_one(new_report)
        elif last_report['hash'] != new_report['hash']:
            self.link('__audit__').insert_one(new_report)
            return False
        return True

    def get_col_stats(self, col: str) -> dict:
        """
            Get the statistics of a collection in the database.

            Args:
                col (str): The name of the collection.

            Returns:
                dict: The statistics of the collection.
        """
        self._link(col)
        return self.db.command('collstats', col)

    def get_db_stats(self) -> dict:
        """
              Get the statistics of the database.

              Returns:
                  dict: The statistics of the database.
        """
        return self.db.command('dbstats')

    def get_cols_name(self) -> List[str]:
        """
              Get the names of all collections in the database.

              Returns:
                  list: The names of the collections.
        """
        return self.db.list_collection_names()

    def _to_df_base(
            self,
            col: str,
            match: dict = None,
            projection: dict = None,
            sort: dict = None,
            skip: dict = 0,
            limit: dict = 0) -> pd.DataFrame:
        self._link(col)
        return df_creator(
            list(
                self.col[col].find(
                    filter = match,
                    projection = projection,
                    sort = sort,
                    skip = skip,
                    limit = limit)))

    def _to_df_large(
            self,
            col: str,
            match: dict = None,
            projection: dict = None,
            verbose = True) -> pd.DataFrame:
        """
            Convert a large collection into a DataFrame by splitting it into multiple parts.

            Args:
                col (str): The name of the collection.
                match (dict, optional): The query filter. Defaults to None.
                projection (dict, optional): The projection query. Defaults to None.
                verbose (bool, optional): Whether to display progress messages. Defaults to True.

            Returns:
                pandas.DataFrame: The DataFrame created from the collection data.
        """

        self._link(col)
        col_status: dict = self.get_col_stats(col)
        st_size: float = col_status['size'] / 1024 ** 2
        st_count: int = col_status['count']
        n: int = math.ceil(st_size / 200)
        step: int = math.ceil(st_count / n)

        if n > 1:
            if verbose:
                print(
                    f'{col} has {st_count:,d} records, {st_size:,.2f} MB, split to {n} parts')
            mem: int = psutil.virtual_memory()
            if mem.total < col_status['size']:
                raise MemoryError(
                    'Not enough memory to process {col}'.format(
                        col = col))

            if mem.available < col_status['size']:
                warnings.warn(
                    'Please note that there may be insufficient memory when reading the {col} in the current system '
                    'environment.'.format(
                        col = col))

            dfs: List[pd.DataFrame] = []

            for i in range(n):
                if verbose:
                    print('processing {i:>2d} part ...'.format(i = i + 1))
                _df: pd.DataFrame = self._to_df_base(
                    col, match = match, projection = projection, skip = i * step, limit = step)
                dfs.append(_df)
            df: pd.DataFrame = pd.concat(dfs)
            if verbose:
                print('done')

        else:
            if verbose:
                print(
                    '{col} has {count:,d} records, {size:,.2f} MB, processing ...'.format(
                        col = col, count = st_count, size = st_size))
            df: pd.DataFrame = self._to_df_base(
                col, match = match, projection = projection)

        return df

    def to_df(
            self,
            col: str,
            match: dict = None,
            projection: dict = None,
            sort: str = None,
            skip: int = 0,
            limit: int = 0) -> pd.DataFrame:
        """
        Convert the data from a collection into a DataFrame.

        Args:
            col (str): The name of the collection.
            match (dict, optional): The query filter. Defaults to None.
            projection (dict, optional): The projection query. Defaults to None.
            sort (list, optional): The sort order. Defaults to None.
            skip (int, optional): The number of documents to skip. Defaults to 0.
            limit (int, optional): The maximum number of documents to return. Defaults to 0.

        Returns:
            pandas.DataFrame: The DataFrame created from the collection data.
        """

        if not any((match, projection, sort, limit, skip)):
            return self._to_df_large(col)
        else:
            return self._to_df_base(col, match, projection, sort, skip, limit)

    def to_df_many(
            self,
            cols: List[str],
            match: dict = None,
            projection: dict = None) -> pd.DataFrame:
        """
         Convert multiple collections into a single DataFrame.

         Args:
             cols (list): The names of the collections.
             match (dict, optional): The query filter. Defaults to None.
             projection (dict, optional): The projection query. Defaults to None.

         Returns:
             pandas.DataFrame: The DataFrame created from the collections' data.
         """
        dfs: List[pd.DataFrame] = [self.to_df(
            c, match = match, projection = projection) for c in cols]
        df: pd.DataFrame = pd.concat(dfs)
        df.reset_index(inplace = True, drop = True)
        return df

    def insert_df(self, df: pd.DataFrame, col: str) -> None:
        """
          Insert a DataFrame into a collection.

          Args:
              df (pandas.DataFrame): The DataFrame to be inserted.
              col (str): The name of the collection.
        """
        self._link(col)
        data: List[dict] = df.to_dict('records')
        self.col[col].insert_many(data)

    def update_df(self, df: pd.DataFrame, col: str, key: str) -> None:
        """
            Update documents in a collection using data from a DataFrame.

            Args:
                df (pandas.DataFrame): The DataFrame containing the updated data.
                col (str): The name of the collection.
                key (str): The key field used to match and update documents.
        """
        # 创建一个空的批量操作列表
        bulk_operations = []

        # 为每条记录创建一个UpdateOne操作，并添加到批量操作列表中
        for record in data:
            filter = {key: record[key]}  # 定位需要更新的文档
            update = {'$set': record}  # 定义更新操作
            bulk_operations.append(pymongo.UpdateOne(filter, update, upsert = True))

        # 执行批量操作
        if bulk_operations:  # 确保有操作要执行
            result = self.col[col].bulk_write(bulk_operations)
            print(f"Bulk operation completed. Matched: {result.matched_count}, "
                  f"Modified: {result.modified_count}, "
                  f"Upserted: {result.upserted_count}")
        else:
            print("No operations to perform.")

    def collection_sample(
            self,
            col: str,
            sample_size: int = 100) -> pd.DataFrame:
        """
        Get a sample of documents from a collection.

        Args:
            col (str): The name of the collection.
            sample_size (int, optional): The number of documents to retrieve. Defaults to 100.

        Returns:
            pandas.DataFrame: The sampled data as a DataFrame.
        """
        return self.to_df(col, limit = sample_size)

    def data_insert(self, col: str, data: dict or list) -> None:
        """
        Insert data into a collection.

        Args:
            col (str): The name of the collection.
            data (dict): The data to be inserted.
        """
        self._link(col)
        _func: Callable[[str], object] = self.col[col].insert_one if isinstance(
            data, dict) else self.col[col].insert_many
        _func(data)

    def drop_col(self, col: str) -> None:
        """
        Drop a collection from the database.

        Args:
            col (str): The name of the collection to be dropped.
        """
        self._link(col)
        self.col[col].dorp()

    def audit_many(self, cols: List[str]) -> List[str]:
        """
        Audit multiple collections in the database.

        Args:
            cols (list): The names of the collections.

        Returns:
            list: The names of the collections that have not pass audited.
        """
        return [col_name for col_name in cols if not self._audit(col_name)]

    def audit_one(self, col: str) -> bool:
        """
        Audit a collection in the database.

        Args:
            col (str): The name of the collection.

        Returns:
            bool: True if the collection has passed the audit, False otherwise.
        """
        return self._audit(col)

    def audit_db(self) -> List[str]:
        """
        Audit all collections in the database.

        Returns:
            list: The names of the collections that have not pass audited.
        """
        col_names: List[str] = self.get_cols_name()
        col_names.remove('__audit__')
        col_names.remove('__log__')
        col_names.remove('system.indexes')
        return self.audit_many(col_names)

    def logging(self, data: dict, _type = '') -> None:
        """
        Insert a log entry into the database.

        Args:
            data (dict): The log data to be inserted.
        """
        data['_type_'] = type
        self.link('__log__').insert_one(data)

    def read_logging(self, _type: str) -> pd.DataFrame:
        return self.link('__log__').find_all({"_type_": _type})

    def __del__(self):
        self.client.close()

    def __repr__(self):
        return f"DBWorker({self.db_code})"
