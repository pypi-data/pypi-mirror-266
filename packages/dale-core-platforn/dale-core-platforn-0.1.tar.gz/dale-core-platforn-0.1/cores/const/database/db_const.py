from ..__const import Const


class DatabaseConst(Const):
    POSTGRESQLDB = 'postgresql'
    MYSQLDB = 'mysql'
    MONGODB = 'mongodb'
    REDISDB = 'redisdb'
    POSTGRESQLDB_CONN = 'PostgresConnection'
    MYSQLDB_CONN = 'MySQLConnection'
    MONGODB_CONN = 'MongoDBConnection'
    REDISDB_CONN = 'RedisDBConnection'
