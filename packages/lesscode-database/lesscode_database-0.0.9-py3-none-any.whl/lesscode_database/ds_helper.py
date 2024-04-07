import importlib
import random
from asyncio import current_task
from contextlib import contextmanager, asynccontextmanager

from lesscode_database.db_options import db_options
from lesscode_database.db_request import sync_common_request, async_common_request


class DsHelper:
    def __init__(self, pool_name):
        self.pool, self.connect_info = getattr(db_options, pool_name)

    def exec(self, method: str, *args, **kwargs):
        return getattr(self.pool, method)(*args, **kwargs)

    async def async_exec(self, method: str, *args, **kwargs):
        return await getattr(self.pool, method)(*args, **kwargs)

    @contextmanager
    def make_sqlalchemy_session(self, **kwargs):
        try:
            sqlalchemy_orm = importlib.import_module("sqlalchemy.orm")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        session = None
        try:
            db_session = sqlalchemy_orm.scoped_session(sqlalchemy_orm.sessionmaker(bind=self.pool, **kwargs))
            session = db_session()
            yield session
        except Exception:
            if session:
                session.rollback()
        else:
            session.commit()
        finally:
            if session:
                session.close()

    @asynccontextmanager
    async def async_make_sqlalchemy_session(self, **kwargs):
        try:
            sqlalchemy_asyncio = importlib.import_module("sqlalchemy.ext.asyncio")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        session = None
        try:
            session = sqlalchemy_asyncio.async_scoped_session(
                sqlalchemy_asyncio.async_sessionmaker(self.pool, **kwargs), current_task)
            yield session
        except Exception:
            if session:
                await session.rollback()
        else:
            await session.commit()
        finally:
            if session:
                await session.close()

    @contextmanager
    def make_neo4j_session(self, **kwargs):
        session = None
        try:
            session = self.pool.session(database=self.connect_info.db_name, **kwargs)
            yield session
        except Exception as e:
            raise e
        finally:
            if session:
                session.close()

    @asynccontextmanager
    async def async_make_neo4j_session(self, **kwargs):
        session = None
        try:
            session = self.pool.session(database=self.connect_info.db_name, **kwargs)
            yield session
        except Exception as e:
            raise e
        finally:
            if session:
                await session.close()

    def make_nebula_session(self, **kwargs):
        try:
            session = self.pool.session_context(user_name=self.connect_info.user, password=self.connect_info.password,
                                                **kwargs)
            return session
        except Exception as e:
            raise e

    def exec_nebula_gql(self, sql, space=None):
        space = space if space else self.connect_info.db_name
        if not space:
            raise Exception(f"nebula no selection space")
        with self.make_nebula_session() as session:
            session.execute(f'USE {space}')
            result = session.execute(sql)
        return result

    def esapi(self, method, path, params=None, data=None, json=None, **kwargs):
        hosts = self.pool["hosts"]
        auth = self.pool["auth"]
        random.shuffle(hosts)
        num = len(hosts)
        res = None
        for i, host in enumerate(hosts):
            url = f"{host}{path}"
            try:
                res = sync_common_request(method=method, url=url, params=params, data=data, json=json,
                                          result_type="json", auth=auth, **kwargs)
                if res:
                    if res.get("took"):
                        break
            except Exception as e:
                if i == num - 1:
                    raise e
        return res

    async def async_esapi(self, method, path, params=None, data=None, json=None, **kwargs):
        hosts = self.pool["hosts"]
        auth = self.pool["auth"]
        random.shuffle(hosts)
        num = len(hosts)
        res = None
        for i, host in enumerate(hosts):
            url = f"{host}{path}"
            try:
                res = await async_common_request(method=method, url=url, params=params, data=data, json=json,
                                                 result_type="json", auth=auth, **kwargs)
                if res:
                    if res.get("took"):
                        break
            except Exception as e:
                if i == num - 1:
                    raise e
        return res
