import psycopg2
import pymongo
import mysql.connector
import redis
from typing import List

from cores.utils.common.store_util import GetUtil
from cores.utils.common.string_util import StringUtil
from cores.utils.common.logger_util import logger


from cores.decorators import parse_db_config
from cores.const.common import EnvConst as const

from cores.model import DbConnModel


class SQLQuery:

    @parse_db_config(const.Database.MYSQL)
    def __init__(self):
        self.__mysql: DbConnModel = GetUtil.suite_get(const.Database.DB_OBJ)
        self.conn = mysql.connector.connect(
            host=self.__mysql.db_host,
            user=self.__mysql.db_username,
            password=StringUtil.base64_decode_text(self.__mysql.db_pwd)
        )

    def execute_statement(self, statement: str = None):
        """
        Execute sql statement
        :param statement: sql query
        :return: result in json format
        """
        if statement:
            logger.debug(f'[SQL] Execute Statement:\n {statement}')
            cursor = self.conn.cursor()
            cursor.execute(statement)
            r = cursor.fetchall()
            # close cursor connection to db right after return data.
            cursor.close()
            logger.debug(f'[SQL] Result: \n{r}')
            return r
        else:
            raise ValueError('No Statement found!')

    def __del__(self):
        """
        Terminate connection to the DB
        """
        self.conn.close()


class RedisQuery:

    @parse_db_config(const.Database.REDIS)
    def __init__(self):
        self.__redis: DbConnModel = GetUtil.suite_get(const.Database.DB_OBJ)
        self.conn = redis.Redis(host=self.__redis.db_host,
                                port=self.__redis.db_port,
                                username=self.__redis.db_username,
                                password=self.__redis.db_pwd,
                                decode_responses=True)

    def get(self, v: str) -> List:
        r = self.conn.get(v)
        logger.debug(f'[Redis] Result: \n{[r]}')
        return [r]

    def set(self, data: dict):
        logger.debug('[Redis] Insert data ')
        for k, v in data.items():
            self.conn.set(k, v)

    def flush_all(self):
        logger.debug('[Redis] Flush all data!')
        self.conn.flushdb()

    def __del__(self):
        self.conn.close()


class MongoDBQuery:

    @parse_db_config(const.Database.MONGODB)
    def __init__(self):
        self.__mongodb: DbConnModel = GetUtil.suite_get(const.Database.DB_OBJ)
        __myclient = pymongo.MongoClient(
            f"mongodb://{self.__mongodb.db_host}:{self.__mongodb.db_port}/")
        self.conn = __myclient[self.__mongodb.db_name]

    def insert(self, table: str, data: list):
        logger.debug(f'[MongoDB] Insert data to {table}:\n {data}')
        if len(data) == 1:
            self.conn[table].insert_one(data[0])
        else:
            self.conn[table].insert_many(data)

    def query(self, table: str, query: dict = None, limit: int = 10) -> list[dict]:
        logger.debug(f'[MongoDB] Execute Statement in {table}:\n{query}')
        if query:
            r = [x for x in self.conn[table].find(query).limit(limit)]
        else:  # return all results limit at limit
            r = [x for x in self.conn[table].find().limit(limit)]
        logger.debug(f'[MongoDB] Result:\n{r}')
        return r

    def truncate_data(self, table: str):
        logger.debug(f'[MongoDB] Truncate all data in {table}!')
        self.conn[table].delete_many({})


class PostgresQuery:

    @parse_db_config(const.Database.POSTGRES)
    def __init__(self):
        self.__postgres: DbConnModel = GetUtil.suite_get(const.Database.DB_OBJ)
        try:
            self.conn = psycopg2.connect(database=self.__postgres.db_name,
                                        user=self.__postgres.db_username,
                                        host=self.__postgres.db_host,
                                        password=self.__postgres.db_pwd)
        except (psycopg2.DatabaseError, Exception) as error:
            raise(error)


    def query(self, command: str):
        logger.info(f'[Postgres] Executed query:\n{command}')
        cur = self.conn.cursor()
        cur.execute(command)
        rows = cur.fetchall()
        logger.debug(f'[Postgres] Result:\n{rows}')
        return rows
    
    def query_first_row(self, command: str):
        logger.info(f'[Postgres] Executed query:\n{command}')
        cur = self.conn.cursor()
        cur.execute(command)
        row = cur.fetchone()
        logger.debug(f'[Postgres] Result:\n{row}')
        return row
    
    def insert_data(self, command: str):
        logger.info(f'[Postgres] Executed query:\n{command}')
        cur = self.conn.cursor()
        cur.execute(command)
        self.conn.commit()

    def __del__(self):
        self.conn.close()
