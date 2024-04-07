# -*- coding: utf-8 -*-
from typing import Any


class ConnectionInfo:
    """
    数据库连接信息对象
    """

    def __init__(self, dialect: str, dsn: str = None, host: str = None, port: int = None, user: str = None,
                 password: str = None,
                 db_name: Any = None, name: str = None, params: dict = None, min_size: int = 3, max_size: int = 10,
                 enable: bool = True, async_enable: bool = False, connect_keepalive: bool = True):
        # 数据库dialect类型
        self.dialect = dialect
        # 连接池名称
        if name:
            self.name = name
        else:
            self.name = dialect
        # dsn
        self.dsn = dsn
        # 主机地址
        self.host = host
        # 端口号
        self.port = port
        # 用户名
        self.user = user
        # 密码
        self.password = password
        # 数据库名称
        self.db_name = db_name
        # 额外参数
        self.params = params
        # 最小数
        self.min_size = min_size
        # 最大数
        self.max_size = max_size
        # 是否启用
        self.enable = enable
        # 是否启用异步
        self.async_enable = async_enable
        # 是否启用session
        self.connect_keepalive = connect_keepalive
