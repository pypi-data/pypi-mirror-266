# -*- coding: utf-8 -*-
import asyncio
import importlib
import ssl
from inspect import iscoroutine

from lesscode_database.connection_info import ConnectionInfo
from lesscode_database.db_request import get_basic_auth


class Pool:
    """
    Elasticsearch 数据库链接创建类
    """

    @staticmethod
    async def create_es_pool(conn_info: ConnectionInfo):
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接对象信息
        :return:
        """
        if conn_info.dsn:
            hosts = conn_info.dsn
        else:
            host_arr = conn_info.host.split(",")
            protocol = "http"
            if conn_info.params:
                if conn_info.params.get('protocol', 'http'):
                    protocol = conn_info.params.get('protocol', 'http')
            hosts = [f"{protocol}://{conn_info.user}:{conn_info.password}@{host}:{conn_info.port}" for host in host_arr]
        try:
            elasticsearch = importlib.import_module("elasticsearch")
        except ImportError:
            raise ImportError(f"elasticsearch is not exist,run:pip install elasticsearch[async]")
        pool = elasticsearch.AsyncElasticsearch(hosts=hosts)
        return pool

    @staticmethod
    def sync_create_es_pool(conn_info: ConnectionInfo):
        """
        创建elasticsearch 同步连接池
        :param conn_info: 连接对象信息
        :return:
        """
        if conn_info.dsn:
            hosts = conn_info.dsn
        else:
            host_arr = conn_info.host.split(",")
            protocol = "http"
            if conn_info.params:
                if conn_info.params.get('protocol', 'http'):
                    protocol = conn_info.params.get('protocol', 'http')
            hosts = [f"{protocol}://{conn_info.user}:{conn_info.password}@{host}:{conn_info.port}" for host in host_arr]
        try:
            elasticsearch = importlib.import_module("elasticsearch")
        except ImportError:
            raise ImportError(f"elasticsearch is not exist,run:pip install elasticsearch")
        pool = elasticsearch.Elasticsearch(hosts)
        return pool

    @staticmethod
    async def create_esapi_pool(conn_info: ConnectionInfo):
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接对象信息
        :return:
        """
        if conn_info.dsn:
            hosts = conn_info.dsn
        else:
            host_arr = conn_info.host.split(",")
            protocol = "http"
            if conn_info.params:
                if conn_info.params.get('protocol', 'http'):
                    protocol = conn_info.params.get('protocol', 'http')
            hosts = [f"{protocol}://{host}:{conn_info.port}" for host in host_arr]
        auth = None
        if conn_info.user and conn_info.password:
            auth = get_basic_auth(conn_info.user, conn_info.password)
        pool = {
            "hosts": hosts,
            "auth": auth
        }
        return pool

    @staticmethod
    def sync_create_esapi_pool(conn_info: ConnectionInfo):
        """
        创建elasticsearch 同步连接池
        :param conn_info: 连接对象信息
        :return:
        """
        if conn_info.dsn:
            hosts = conn_info.dsn
        else:
            host_arr = conn_info.host.split(",")
            protocol = "http"
            if conn_info.params:
                if conn_info.params.get('protocol', 'http'):
                    protocol = conn_info.params.get('protocol', 'http')
            hosts = [f"{protocol}://{host}:{conn_info.port}" for host in host_arr]
        auth = None
        if conn_info.user and conn_info.password:
            auth = get_basic_auth(conn_info.user, conn_info.password)
        pool = {
            "hosts": hosts,
            "auth": auth
        }
        return pool

    @staticmethod
    def create_mongo_pool(conn_info: ConnectionInfo):
        """
        创建mongodb 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            motor_asyncio = importlib.import_module("motor.motor_asyncio")
        except ImportError:
            raise ImportError(f"motor is not exist,run:pip install motor")
        if conn_info.dsn:
            uri = conn_info.dsn
        else:
            host_str = conn_info.host.split(",")
            hosts = ",".join([f"{host}:{conn_info.port}" for host in host_str])
            uri = f"mongodb://{conn_info.user}:{conn_info.password}@{hosts}"
            if conn_info.params:
                auth_type = conn_info.params.get("type")
                if auth_type == "LDAP":
                    uri += "/?authMechanism=PLAIN"
                elif auth_type == "Password":
                    uri += "/?authSource=admin"
                elif auth_type == "X509":
                    uri += "/?authMechanism=MONGODB-X509"
        pool = motor_asyncio.AsyncIOMotorClient(uri)
        return pool

    @staticmethod
    def sync_create_mongo_pool(conn_info: ConnectionInfo):
        """
        创建mongodb 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            pymongo = importlib.import_module("pymongo")
        except ImportError:
            raise ImportError(f"pymongo is not exist,run:pip install pymongo")
        if conn_info.dsn:
            uri = conn_info.dsn
        else:
            host_str = conn_info.host.split(",")
            hosts = ",".join([f"{host}:{conn_info.port}" for host in host_str])
            uri = f"mongodb://{conn_info.user}:{conn_info.password}@{hosts}"
            if conn_info.params:
                auth_type = conn_info.params.get("type")
                if auth_type == "LDAP":
                    uri += "/?authMechanism=PLAIN"
                elif auth_type == "Password":
                    uri += "/?authSource=admin"
                elif auth_type == "X509":
                    uri += "/?authMechanism=MONGODB-X509"
        pool = pymongo.MongoClient(uri)
        return pool

    @staticmethod
    async def create_mysql_pool(conn_info: ConnectionInfo):
        """
        创建mysql 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise ImportError(f"aiomysql is not exist,run:pip install aiomysql")
        pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port,
                                          user=conn_info.user,
                                          password=conn_info.password,
                                          pool_recycle=conn_info.params.get("pool_recycle", 3600)
                                          if conn_info.params else 3600,
                                          db=conn_info.db_name, autocommit=True,
                                          minsize=conn_info.min_size,
                                          maxsize=conn_info.max_size,
                                          cursorclass=aiomysql.DictCursor)
        return pool

    @staticmethod
    def sync_create_mysql_pool(conn_info: ConnectionInfo):
        """
        创建mysql 同步连接池
        :param conn_info: 连接信息
        :return: 
        """
        try:
            pymysql = importlib.import_module("pymysql")
        except ImportError:
            raise ImportError(f"pymysql is not exist,run:pip install pymysql")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=pymysql, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    async def create_sqlite3_pool(conn_info: ConnectionInfo):
        """
        创建mysql 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aiosqlite3 = importlib.import_module("aiosqlite3")
        except ImportError:
            raise ImportError(f"aiosqlite3 is not exist,run:pip install aiosqlite3")
        pool = await aiosqlite3.connect(database=conn_info.dsn)
        return pool

    @staticmethod
    def sync_create_sqlite3_pool(conn_info: ConnectionInfo):
        """
        创建mysql 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            sqlite3 = importlib.import_module("sqlite3")
        except ImportError:
            raise ImportError(f"sqlite3 is not exist,run:pip install sqlite3")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=sqlite3, database=conn_info.dsn,
                                  check_same_thread=False)
        return pool

    @staticmethod
    def sync_create_mssql_pool(conn_info: ConnectionInfo):
        """
        创建mysql 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            pymssql = importlib.import_module("pymssql")
        except ImportError:
            raise ImportError(f"pymssql is not exist,run:pip install pymssql")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=pymssql, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    def sync_create_oracle_pool(conn_info: ConnectionInfo):
        """
        创建mysql 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            cx_oracle = importlib.import_module("cx_Oracle")
        except ImportError:
            raise ImportError(f"cx_Oracle is not exist,run:pip install cx_Oracle")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=cx_oracle, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    async def create_doris_pool(conn_info: ConnectionInfo):
        """
        创建doris 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise ImportError(f"aiomysql is not exist,run:pip install aiomysql")
        pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port,
                                          user=conn_info.user,
                                          password=conn_info.password,
                                          pool_recycle=conn_info.params.get("pool_recycle", 3600)
                                          if conn_info.params else 3600,
                                          db=conn_info.db_name, autocommit=True,
                                          minsize=conn_info.min_size,
                                          maxsize=conn_info.max_size)
        return pool

    @staticmethod
    def sync_create_doris_pool(conn_info: ConnectionInfo):
        """
        创建doris 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            pymysql = importlib.import_module("pymysql")
        except ImportError:
            raise ImportError(f"pymysql is not exist,run:pip install pymysql")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=pymysql, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    async def create_tidb_pool(conn_info: ConnectionInfo):
        """
        创建tidb 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise ImportError(f"aiomysql is not exist,run:pip install aiomysql")
        pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port,
                                          user=conn_info.user,
                                          password=conn_info.password,
                                          pool_recycle=conn_info.params.get("pool_recycle", 3600)
                                          if conn_info.params else 3600,
                                          db=conn_info.db_name, autocommit=True,
                                          minsize=conn_info.min_size,
                                          maxsize=conn_info.max_size)
        return pool

    @staticmethod
    def sync_create_tidb_pool(conn_info: ConnectionInfo):
        """
        创建tidb 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            pymysql = importlib.import_module("pymysql")
        except ImportError:
            raise ImportError(f"pymysql is not exist,run:pip install pymysql")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=pymysql, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    async def create_ocean_base_pool(conn_info: ConnectionInfo):
        """
        创建ocean_base 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise ImportError(f"aiomysql is not exist,run:pip install aiomysql")
        pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port,
                                          user=conn_info.user,
                                          password=conn_info.password,
                                          pool_recycle=conn_info.params.get("pool_recycle", 3600)
                                          if conn_info.params else 3600,
                                          db=conn_info.db_name, autocommit=True,
                                          minsize=conn_info.min_size,
                                          maxsize=conn_info.max_size)
        return pool

    @staticmethod
    def sync_create_ocean_base_pool(conn_info: ConnectionInfo):
        """
        创建ocean_base 同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            pymysql = importlib.import_module("pymysql")
        except ImportError:
            raise ImportError(f"pymysql is not exist,run:pip install pymysql")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(creator=pymysql, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  passwd=conn_info.password, db=conn_info.db_name,
                                  mincached=conn_info.min_size, blocking=True, maxusage=conn_info.min_size,
                                  maxshared=conn_info.max_size, maxcached=conn_info.max_size,
                                  ping=1, maxconnections=conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool

    @staticmethod
    def sync_create_nebula_pool(conn_info: ConnectionInfo):
        """
        创建nebula3连接池
        :param conn_info: 连接信息
        :return: 
        """
        try:
            nebula3_gclient_net = importlib.import_module("nebula3.gclient.net")
            nebula3_config = importlib.import_module("nebula3.Config")
        except ImportError:
            raise ImportError(f"nebula3 is not exist,run:pip install nebula3-python")
        config = nebula3_config.Config()
        ssl_conf = None
        config.max_connection_pool_size = conn_info.max_size
        config.min_connection_pool_size = conn_info.min_size
        if conn_info.params and isinstance(conn_info.params, dict):
            config.timeout = conn_info.params.get("timeout", 0)
            config.idle_time = conn_info.params.get("idle_time", 0)
            config.interval_check = conn_info.params.get("interval_check", -1)
            ssl_config = conn_info.params.get("ssl_conf", {})
            if ssl_conf and isinstance(ssl_conf, dict):
                ssl_conf = nebula3_config.SSL_config()
                ssl_conf.unix_socket = ssl_config.get("unix_socket", None)
                ssl_conf.ssl_version = ssl_config.get("ssl_version", None)
                ssl_conf.cert_reqs = ssl_config.get("cert_reqs", ssl.CERT_NONE)
                ssl_conf.ca_certs = ssl_config.get("ca_certs", None)
                ssl_conf.verify_name = ssl_config.get("verify_name", None)
                ssl_conf.keyfile = ssl_config.get("keyfile", None)
                ssl_conf.certfile = ssl_config.get("certfile", None)
                ssl_conf.allow_weak_ssl_versions = ssl_config.get("allow_weak_ssl_versions", None)
        pool = nebula3_gclient_net.ConnectionPool()
        pool.init([(conn_info.host, conn_info.port)], config, ssl_conf)
        return pool

    @staticmethod
    async def create_neo4j_pool(conn_info: ConnectionInfo):
        """
        创建Neo4j异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            neo4j = importlib.import_module("neo4j")
        except ImportError:
            raise ImportError(f"neo4j is not exist,run:pip install neo4j")
        if conn_info.dsn:
            uri = conn_info.dsn
        else:
            uri = f"bolt://{conn_info.host}:{conn_info.port}"
        driver = neo4j.AsyncGraphDatabase.driver(uri, auth=(conn_info.user, conn_info.password))
        return driver

    @staticmethod
    def sync_create_neo4j_pool(conn_info: ConnectionInfo):
        """
        创建Neo4j同步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            neo4j = importlib.import_module("neo4j")
        except ImportError:
            raise ImportError(f"neo4j is not exist,run:pip install neo4j")
        if conn_info.dsn:
            uri = conn_info.dsn
        else:
            uri = f"bolt://{conn_info.host}:{conn_info.port}"
        driver = neo4j.GraphDatabase.driver(uri, auth=(conn_info.user, conn_info.password))
        return driver

    @staticmethod
    async def create_postgresql_pool(conn_info: ConnectionInfo):
        """
        创建postgresql 异步连接池
        :param conn_info: 连接信息
        :return: 
        """
        try:
            aiopg = importlib.import_module("aiopg")
        except ImportError:
            raise ImportError(f"aiopg is not exist,run:pip install aiopg")
        pool = await aiopg.create_pool(dsn=conn_info.dsn, host=conn_info.host, port=conn_info.port, user=conn_info.user,
                                       password=conn_info.password,
                                       database=conn_info.db_name)
        return pool

    @staticmethod
    def sync_create_postgresql_pool(conn_info: ConnectionInfo):
        """
        创建postgresql 同步连接池
        :param conn_info: 连接信息
        :return: 
        """
        try:
            psycopg2 = importlib.import_module("psycopg2")
        except ImportError:
            raise ImportError(f"psycopg2-binary is not exist,run:pip install psycopg2-binary")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise ImportError(f"DBUtils is not exist,run:pip install DBUtils")
        pool = pooled_db.PooledDB(psycopg2, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  password=conn_info.password, database=conn_info.db_name)
        return pool

    @staticmethod
    def create_redis_pool(conn_info: ConnectionInfo):
        """
        创建redis异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            aioredis = importlib.import_module("aioredis")
        except ImportError:
            raise ImportError(f"aioredis is not exist,run:pip install aioredis")
        if not conn_info.dsn:
            conn_info.dsn = "redis://"
        pool = aioredis.ConnectionPool.from_url(url=conn_info.dsn, host=conn_info.host, port=conn_info.port,
                                                username=conn_info.user, password=conn_info.password,
                                                db=conn_info.db_name, encoding="utf-8", decode_responses=True)
        return aioredis.Redis(connection_pool=pool, decode_responses=True)

    @staticmethod
    def sync_create_redis_pool(conn_info: ConnectionInfo):
        """
        创建redis同步连接池
        :param conn_info:连接信息
        :return:
        """
        try:
            redis = importlib.import_module("redis")
        except ImportError:
            raise ImportError(f"redis is not exist,run:pip install redis")
        if not conn_info.dsn:
            conn_info.dsn = "redis://"
        pool = redis.ConnectionPool.from_url(url=conn_info.dsn, host=conn_info.host, port=conn_info.port,
                                             username=conn_info.user, password=conn_info.password,
                                             db=conn_info.db_name, encoding="utf-8", decode_responses=True)
        return redis.Redis(connection_pool=pool, decode_responses=True)

    @staticmethod
    async def create_redis_cluster_pool(conn_info: ConnectionInfo):
        """
        创建redis cluster异步连接池
        :param conn_info:连接信息
        :return:
        """
        try:
            aioredis_cluster = importlib.import_module("aioredis_cluster")
        except ImportError:
            raise ImportError(f"aioredis is not exist,run:pip install aioredis-cluster")
        params = conn_info.params if conn_info.params else {}
        retry_min_delay = params.get("retry_min_delay")
        retry_max_delay = params.get("retry_max_delay")
        max_attempts = params.get("max_attempts")
        state_reload_interval = params.get("state_reload_interval")
        follow_cluster = params.get("follow_cluster")
        idle_connection_timeout = params.get("idle_connection_timeout")
        username = params.get("username")
        password = conn_info.password
        encoding = params.get("encoding")
        connect_timeout = params.get("connect_timeout")
        attempt_timeout = params.get("attempt_timeout")
        ssl_info = params.get("ssl")
        pool = await aioredis_cluster.create_redis_cluster(startup_nodes=conn_info.dsn,
                                                           retry_min_delay=retry_min_delay,
                                                           retry_max_delay=retry_max_delay,
                                                           max_attempts=max_attempts,
                                                           state_reload_interval=state_reload_interval,
                                                           follow_cluster=follow_cluster,
                                                           idle_connection_timeout=idle_connection_timeout,
                                                           username=username,
                                                           password=password,
                                                           encoding=encoding,
                                                           pool_minsize=conn_info.min_size,
                                                           pool_maxsize=conn_info.max_size,
                                                           connect_timeout=connect_timeout,
                                                           attempt_timeout=attempt_timeout,
                                                           ssl=ssl_info)
        return pool

    @staticmethod
    def sync_create_redis_cluster_pool(conn_info: ConnectionInfo):
        """
        创建redis cluster同步连接池
        :param conn_info:连接信息
        :return:
        """
        try:
            rediscluster = importlib.import_module("rediscluster")
        except ImportError:
            raise ImportError(f"redis is not exist,run:pip install redis-py-cluster")
        params = conn_info.params if conn_info.params else {}
        init_slot_cache = params.get("init_slot_cache", True) if params else True
        max_connections_per_node = params.get("init_slot_cache",
                                              False) if params else False

        skip_full_coverage_check = params.get("skip_full_coverage_check",
                                              False) if params else False
        nodemanager_follow_cluster = params.get("nodemanager_follow_cluster",
                                                False) if params else False
        host_port_remap = params.get("nodemanager_follow_cluster",
                                     None) if params else None
        pool = rediscluster.ClusterConnectionPool(startup_nodes=conn_info.dsn, init_slot_cache=init_slot_cache,
                                                  max_connections=conn_info.max_size,
                                                  max_connections_per_node=max_connections_per_node,
                                                  skip_full_coverage_check=skip_full_coverage_check,
                                                  nodemanager_follow_cluster=nodemanager_follow_cluster,
                                                  host_port_remap=host_port_remap, db=conn_info.db_name,
                                                  username=conn_info.user, password=conn_info.password)
        return pool

    @staticmethod
    async def create_clickhouse_pool(conn_info: ConnectionInfo):
        try:
            asynch = importlib.import_module("asynch")
        except ImportError:
            raise ImportError(f"asynch is not exist,run:pip install asynch")
        pool = await asynch.create_pool(minsize=conn_info.min_size, maxsize=conn_info.max_size,
                                        dsn=conn_info.dsn, host=conn_info.host,
                                        user=conn_info.user, password=conn_info.password,
                                        port=conn_info.port, database=conn_info.db_name)
        return pool

    @staticmethod
    def sync_create_clickhouse_pool(conn_info: ConnectionInfo):
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise Exception(f"DBUtils is not exist,run:pip install DBUtils==3.0.2")
        try:
            clickhouse_driver = importlib.import_module("clickhouse_driver")
        except ImportError:
            raise Exception(f"clickhouse_driver is not exist,run:pip install clickhouse_driver")
        params = conn_info.params
        if not isinstance(params, dict):
            params = dict()

        pool = pooled_db.PooledDB(creator=clickhouse_driver.connect, host=conn_info.host, port=conn_info.port,
                                  user=conn_info.user,
                                  password=conn_info.password, database=conn_info.db_name or "default",
                                  **params)
        return pool

    @staticmethod
    def create_sqlalchemy_pool(conn_info: ConnectionInfo):
        """
        创建sqlalchemy同步连接池
        :param conn_info: 连接信息
        :return:
        """
        if conn_info.dsn:
            url = conn_info.dsn
        else:
            db_type = "mysql"
            if conn_info.params:
                if conn_info.params.get("db_type"):
                    db_type = conn_info.params.pop("db_type")
            if db_type == "mysql":
                url = 'mysql+aiomysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "postgresql":
                url = 'postgresql+aiopg://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "tidb":
                url = 'mysql+aiomysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "ocean_base":
                url = 'mysql+aiomysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "doris":
                url = 'mysql+aiomysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            else:
                raise ImportError("UNSUPPORTED DB TYPE")
        try:
            sqlalchemy = importlib.import_module("sqlalchemy.ext.asyncio")
        except ImportError:
            raise ImportError(f"sqlalchemy is not exist,run:pip install sqlalchemy")
        engine = sqlalchemy.create_async_engine(url, echo=conn_info.params.get("echo",
                                                                               True) if conn_info.params else True,
                                                pool_size=conn_info.min_size,
                                                pool_recycle=conn_info.params.get("pool_recycle",
                                                                                  3600) if conn_info.params else 3600,
                                                max_overflow=conn_info.params.get("max_overflow",
                                                                                  0) if conn_info.params else 0,
                                                pool_timeout=conn_info.params.get("pool_timeout",
                                                                                  10) if conn_info.params else 10,
                                                pool_pre_ping=conn_info.params.get("pool_pre_ping",
                                                                                   True) if conn_info.params else True)
        return engine

    @staticmethod
    def sync_create_sqlalchemy_pool(conn_info: ConnectionInfo):
        """
        创建sqlalchemy同步连接池
        :param conn_info: 连接信息
        :return:
        """
        if conn_info.dsn:
            url = conn_info.dsn
        else:
            db_type = "mysql"
            if conn_info.params:
                if conn_info.params.get("db_type"):
                    db_type = conn_info.params.pop("db_type")
            if db_type == "mysql":
                url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "postgresql":
                url = 'postgresql+psycopg2://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "tidb":
                url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "ocean_base":
                url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "doris":
                url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "sqlite3":
                url = conn_info.dsn
            elif db_type == "mssql":
                url = "mssql+pymssql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            elif db_type == "oracle":
                url = "oracle+cx_oracle://{}:{}@{}:{}/{}?charset=utf8mb4".format(
                    conn_info.user, conn_info.password, conn_info.host, conn_info.port,
                    conn_info.db_name)
            else:
                raise ImportError("UNSUPPORTED DB TYPE")
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise ImportError(f"sqlalchemy is not exist,run:pip install sqlalchemy")
        engine = sqlalchemy.create_engine(url, echo=conn_info.params.get("echo",
                                                                         True) if conn_info.params else True,
                                          pool_size=conn_info.min_size,
                                          pool_recycle=conn_info.params.get("pool_recycle",
                                                                            3600) if conn_info.params else 3600,
                                          max_overflow=conn_info.params.get("max_overflow",
                                                                            0) if conn_info.params else 0,
                                          pool_timeout=conn_info.params.get("pool_timeout",
                                                                            10) if conn_info.params else 10,
                                          pool_pre_ping=conn_info.params.get("pool_pre_ping",
                                                                             True) if conn_info.params else True)
        return engine

    @staticmethod
    def sync_create_dbutils_pool(conn_info: ConnectionInfo):
        params = conn_info.params
        if not isinstance(params, dict):
            params = dict()
        creator = params.pop("creator")
        try:
            generic = importlib.import_module(creator)
        except ImportError:
            raise Exception(f"{creator} is not exist,run:pip install {creator}")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
            steady_db = importlib.import_module("dbutils.steady_db")
            simple_pooled_db = importlib.import_module("dbutils.simple_pooled_db")
            persistent_db = importlib.import_module("dbutils.persistent_db")
        except ImportError:
            raise Exception(f"DBUtils is not exist,run:pip install DBUtils==3.0.2")
        pool_type = params.pop("pool_type", "PooledDB")
        if pool_type not in ["SimplePooledDB", "SteadyDBConnection", "PersistentDB", "PooledDB"]:
            pool_type = "PooledDB"

        mincached = params.pop("mincached", conn_info.min_size)
        maxusage = params.pop("maxusage", conn_info.min_size)
        maxshared = params.pop("maxshared", conn_info.max_size)
        maxcached = params.pop("maxcached", conn_info.max_size)
        blocking = params.pop("blocking", True)
        reset = params.pop("reset", True)
        setsession = params.pop("setsession", None)
        failures = params.pop("failures", None)
        ping = params.pop("ping", 1)
        threadlocal = params.pop("threadlocal", None)
        closeable = params.pop("closeable", True)
        maxconnections = params.pop("maxconnections", None)
        if pool_type == "SimplePooledDB":
            pool = simple_pooled_db.PooledDB(dbapi=creator, maxconnections=maxconnections, **params)
        elif pool_type == "SteadyDBConnection":
            pool = steady_db.SteadyDBConnection(creator=creator, maxusage=maxusage, setsession=setsession,
                                                failures=failures,
                                                ping=ping, closeable=closeable, **params)
        elif pool_type == "PersistentDB":
            pool = persistent_db.PersistentDB(creator=creator, maxusage=maxusage, setsession=setsession,
                                              failures=failures, ping=ping,
                                              closeable=closeable, threadlocal=threadlocal, **params)
        else:
            pool = pooled_db.PooledDB(creator=generic, mincached=mincached, maxcached=maxcached,
                                      maxshared=maxshared, maxconnections=conn_info.max_size, blocking=blocking,
                                      maxusage=maxusage, setsession=setsession, reset=reset,
                                      failures=failures, ping=ping, **params)
        return pool


def run_sync(func_instance):
    if iscoroutine(func_instance):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(func_instance)
        loop.run_until_complete(future)
        return future.result()
    else:
        return func_instance


def get_pool(conn_info: ConnectionInfo):
    if conn_info.dialect == "elasticsearch":
        if conn_info.async_enable:
            return run_sync(Pool.create_es_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_es_pool(conn_info)), conn_info

    elif conn_info.dialect == "esapi":
        if conn_info.async_enable:
            return run_sync(Pool.create_esapi_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_esapi_pool(conn_info)), conn_info

    elif conn_info.dialect == "mongo":
        if conn_info.async_enable:
            return run_sync(Pool.create_mongo_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_mongo_pool(conn_info)), conn_info

    elif conn_info.dialect == "mysql":
        if conn_info.async_enable:
            return run_sync(Pool.create_mysql_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_mysql_pool(conn_info)), conn_info

    elif conn_info.dialect == "doris":
        if conn_info.async_enable:
            return run_sync(Pool.create_doris_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_doris_pool(conn_info)), conn_info

    elif conn_info.dialect == "ocean_base":
        if conn_info.async_enable:
            return run_sync(Pool.create_ocean_base_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_ocean_base_pool(conn_info)), conn_info

    elif conn_info.dialect == "tidb":
        if conn_info.async_enable:
            return run_sync(Pool.create_tidb_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_tidb_pool(conn_info)), conn_info

    elif conn_info.dialect == "mssql":
        return run_sync(Pool.sync_create_mssql_pool(conn_info)), conn_info

    elif conn_info.dialect == "oracle":
        return run_sync(Pool.sync_create_oracle_pool(conn_info)), conn_info

    elif conn_info.dialect == "nebula":
        return run_sync(Pool.sync_create_nebula_pool(conn_info)), conn_info

    elif conn_info.dialect == "neo4j":
        if conn_info.async_enable:
            return run_sync(Pool.create_neo4j_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_neo4j_pool(conn_info)), conn_info

    elif conn_info.dialect == "postgresql":
        if conn_info.async_enable:
            return run_sync(Pool.create_postgresql_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_postgresql_pool(conn_info)), conn_info

    elif conn_info.dialect == "sqlite3":
        if conn_info.async_enable:
            return run_sync(Pool.create_sqlite3_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_sqlite3_pool(conn_info)), conn_info

    elif conn_info.dialect == "redis":
        if conn_info.async_enable:
            return run_sync(Pool.create_redis_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_redis_pool(conn_info)), conn_info

    elif conn_info.dialect == "redis_cluster":
        if conn_info.async_enable:
            return run_sync(Pool.create_redis_cluster_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_redis_cluster_pool(conn_info)), conn_info

    elif conn_info.dialect == "clickhouse":
        if conn_info.async_enable:
            return run_sync(Pool.create_clickhouse_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_clickhouse_pool(conn_info)), conn_info

    elif conn_info.dialect == "sqlalchemy":
        if conn_info.async_enable:
            return run_sync(Pool.create_sqlalchemy_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_sqlalchemy_pool(conn_info)), conn_info

    elif conn_info.dialect == "dbutils":
        if conn_info.async_enable:
            return run_sync(Pool.sync_create_dbutils_pool(conn_info)), conn_info
        else:
            return run_sync(Pool.sync_create_dbutils_pool(conn_info)), conn_info

    else:
        raise Exception(f"conn_info.dialect={conn_info.dialect} is not supported")
