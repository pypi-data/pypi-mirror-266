from typing import Optional
from sqlalchemy.pool import QueuePool
from pydantic import BaseModel


class DatabaseInfoItem(BaseModel):
    """数据库信息项"""
    # 数据库连接地址, 格式：dialect+driver://username:password@host:port/database， 示例：postgresql://user:pass@localhost/mydatabase
    database_uri: str
    # 是否打印sql， 如果设置为 True，SQLAlchemy 将在控制台输出所有执行的 SQL 语句。
    echo_sql: Optional[bool] = False
    pool_class: Optional[type] = QueuePool
    # 当设置为 True 时，SQLAlchemy 将输出有关连接池操作的日志信息。
    echo_pool: Optional[bool | str] = False
    # 指定连接池的大小。这是连接池中可以保持的活动连接数，连接池中的最小和最大连接数
    pool_size: Optional[int] = 5
    # 指定在连接池耗尽时，可以额外创建的连接数。（在达到pool_size后可以额外创建的连接数）
    pool_max_overflow: Optional[int] = 10
    # 回收时间(秒), 指定连接在被返回到连接池之前应该保持多长时间的打开状态。这有助于确保连接不会因为长时间未使用而被数据库服务器关闭。
    pool_recycle: Optional[int] = 3600
    # 指定当从连接池中获取连接时应该等待多长时间(秒)。如果在这个时间内没有可用的连接，将会抛出一个异常。
    pool_timeout: Optional[int] = 30
    # 预ping检查
    pool_pre_ping: Optional[bool] = True
    # 是否（后进先出）
    pool_use_lifo: Optional[bool] = False
    # 是否自动提交
    auto_commit: Optional[bool] = False
    # 是否自动flush
    auto_flush: Optional[bool] = False
    # 超时是否自动提交
    expire_on_commit: Optional[bool] = False
