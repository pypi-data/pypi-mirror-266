from ...const.database import DatabaseConst
from .database_factory import SQLQuery, PostgresQuery, RedisQuery, MongoDBQuery


class DatabaseFactory(object):
    """
    This Factory to register the method to create connection to database

    :return connection to the desired db
    """
    @staticmethod
    def create_db_connection(db_type: str):
        if db_type == DatabaseConst.POSTGRESQLDB:
            return PostgresQuery()
        elif db_type == DatabaseConst.MYSQLDB:
            return SQLQuery()
        elif db_type == DatabaseConst.MONGODB:
            return MongoDBQuery()
        elif db_type == DatabaseConst.REDISDB:
            return RedisQuery()
        else:
            raise ValueError(f'Not support {db_type}')
