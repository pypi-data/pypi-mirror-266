import re
from typing import Callable

from sqlalchemy import Column, DateTime, Boolean, Float, func, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Connection

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from afeng_tools.sqlalchemy_tools.core.sqlalchemy_items import DatabaseInfoItem
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_meta_class import ModelMetaClass


class SqlalchemyDb:
    """数据库对象"""

    def __init__(self, database_info: DatabaseInfoItem):
        self.database_info = database_info
        self.Base = declarative_base()
        self.BaseModel = self._create_base_model()
        self.is_postgresql = True if re.match('^postgresql', self.database_info.database_uri) else False
        self.Base.is_postgresql = self.is_postgresql
        self.engine = create_engine(self.database_info.database_uri,
                                    echo=self.database_info.echo_sql,
                                    poolclass=self.database_info.pool_class,
                                    echo_pool=self.database_info.echo_pool,
                                    pool_size=self.database_info.pool_size,
                                    max_overflow=self.database_info.pool_max_overflow,
                                    pool_recycle=self.database_info.pool_recycle,
                                    pool_timeout=self.database_info.pool_timeout,
                                    pool_pre_ping=self.database_info.pool_pre_ping,
                                    pool_use_lifo=self.database_info.pool_use_lifo, )
        self.session_maker = sessionmaker(bind=self.engine,
                                          autocommit=self.database_info.auto_commit,
                                          autoflush=self.database_info.auto_flush,
                                          expire_on_commit=self.database_info.expire_on_commit)
        self.async_session_maker = async_sessionmaker(sync_session_class=self.session_maker)

    def _create_base_model(self):
        class BaseModel(self.Base, metaclass=ModelMetaClass):
            """模型根类"""
            __abstract__ = True

            id = Column(BigInteger, comment='主键', primary_key=True, index=True, autoincrement=True)
            add_time = Column(DateTime, comment='添加时间', default=func.now())
            update_time = Column(DateTime, comment='修改时间', default=func.now(), onupdate=func.now())
            is_enable = Column(Boolean, comment='是否可用', default=True)
            order_num = Column(Float, comment='排序值', default=100)

        return BaseModel

    def get_session(self) -> Session:
        """获取Session"""
        return self.session_maker()

    def get_async_session(self) -> AsyncSession:
        """获取异步Session， 使用示例：await async_session.commit()"""
        return self.async_session_maker()

    def get_connection(self) -> Connection:
        """获取Connection, 使用指南：https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection"""
        return self.engine.connect()

    def with_connection(self, work_func: Callable[[Connection, ], None]) -> Session:
        """使用Connection, 使用指南：https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection"""
        with self.engine.connect() as connection:
            work_func(connection)
