from typing import Any, Optional, Callable

from lesscode_database.connect_pool import get_pool
from lesscode_database.connection_info import ConnectionInfo


class DbOptions:
    _instance = None

    def __init__(self):
        self.conn_list = []

    def define(
            self,
            name: str,
            default: Any = None,
            type_: Optional[type] = None,
            help_: Optional[str] = None,
            callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        if hasattr(self, name):
            raise Exception(f'name={name} has been defined')
        if type_:
            if not isinstance(default, type_):
                raise Exception(f'default={default} type is error')
        if callback:
            default = callback(default)
        self.__setattr__(name, {"name": name, "value": default, "help": help_})

    def __getattr__(self, name: str):
        if hasattr(super(), name):
            return super().__getattr__(name)
        raise AttributeError("Unrecognized option %r" % name)

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "conn_list":
            if isinstance(value, list):
                for conn_info in value:
                    if isinstance(conn_info, ConnectionInfo):
                        if conn_info.enable:
                            self.__setattr__(conn_info.name, get_pool(conn_info))

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


db_options = DbOptions()


def db_define(name: str,
              default: Any = None,
              type_: Optional[type] = None,
              help_: Optional[str] = None,
              callback: Optional[Callable[[Any], None]] = None,
              ) -> None:
    return db_options.define(name=name, default=default, type_=type_, help_=help_, callback=callback)
