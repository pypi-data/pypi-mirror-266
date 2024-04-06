from typing import Callable

from afeng_tools.decorator_tool.decorator_tools import run_func
from afeng_tools.log_tool import loguru_tools
from afeng_tools.log_tool.loguru_tools import log_error

from afeng_tools.sqlalchemy_tools import sqlalchemy_settings

logger = loguru_tools.get_logger()


def auto_commit_db(db_code: str = 'default', retry: int = 0):
    """自动注入自动提交的db: Session"""
    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'db' in kwargs:
                return run_func(func, *args, **kwargs)
            tmp_db = None
            args_hava_db_code = False
            args_db_code = None
            if 'db_code' in kwargs:
                args_hava_db_code = True
                args_db_code = kwargs.pop('db_code')
                if args_db_code:
                    tmp_db = sqlalchemy_settings.get_database(db_code=args_db_code)
            if not tmp_db:
                tmp_db = sqlalchemy_settings.get_database(db_code=db_code)
            with tmp_db.get_session() as session:
                try:
                    kwargs['db'] = session
                    result = run_func(func, *args, **kwargs)
                    session.commit()
                    return result
                except Exception as e:
                    logger.error(f'Db session commit data exception, will to retry[{retry}]')
                    session.rollback()
                    if retry > 0:
                        kwargs.pop('db')
                        if args_hava_db_code:
                            kwargs['db_code'] = args_db_code
                        return auto_commit_db(db_code=db_code, retry=retry - 1)(func)(*args, **kwargs)
                    else:
                        raise e
        return wrap
    return auto_wrap


def auto_db(db_code: str = 'default', retry: int = 3):
    """自动注入db: Session"""
    def auto_wrap(func: Callable):
        def wrap(*args, **kwargs):
            if 'db' in kwargs:
                return run_func(func, *args, **kwargs)
            tmp_db = None
            args_hava_db_code = False
            args_db_code = None
            if 'db_code' in kwargs:
                args_hava_db_code = True
                args_db_code = kwargs.pop('db_code')
                if args_db_code:
                    tmp_db = sqlalchemy_settings.get_database(db_code=args_db_code)
            if not tmp_db:
                tmp_db = sqlalchemy_settings.get_database(db_code=db_code)
            with tmp_db.get_session() as session:
                kwargs['db'] = session
                try:
                    return run_func(func, *args, **kwargs)
                except Exception as e:
                    logger.error(f'Db session commit data exception, will to retry[{retry}]')
                    if retry > 0:
                        kwargs.pop('db')
                        if args_hava_db_code:
                            kwargs['db_code'] = args_db_code
                        return auto_db(db_code=db_code, retry=retry-1)(func)(*args, **kwargs)
                    else:
                        raise e
        return wrap

    return auto_wrap


def auto_commit_conn(db_code: str = 'default'):
    """自动注入自动提交的conn: Connection"""

    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'conn' in kwargs:
                return run_func(func, *args, **kwargs)
            tmp_db = None
            if 'db_code' in kwargs:
                session_db_code = kwargs.pop('db_code')
                if session_db_code:
                    tmp_db = sqlalchemy_settings.get_database(db_code=session_db_code)
            if not tmp_db:
                tmp_db = sqlalchemy_settings.get_database(db_code=db_code)
            with tmp_db.engine.connect() as conn:
                try:
                    kwargs['conn'] = conn
                    result = run_func(func, *args, **kwargs)
                    conn.commit()
                    return result
                except Exception as e:
                    logger.error(f'Db connection commit data exception')
                    conn.rollback()
                    raise e

        return wrap

    return auto_wrap


def auto_conn(db_code: str = 'default'):
    """自动注入conn: Connection"""

    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'conn' in kwargs:
                return run_func(func, *args, **kwargs)
            tmp_db = None
            if 'db_code' in kwargs:
                session_db_code = kwargs.pop('db_code')
                if session_db_code:
                    tmp_db = sqlalchemy_settings.get_database(db_code=session_db_code)
            if not tmp_db:
                tmp_db = sqlalchemy_settings.get_database(db_code=db_code)
            with tmp_db.engine.connect() as conn:
                kwargs['conn'] = conn
                return run_func(func, *args, **kwargs)

        return wrap

    return auto_wrap
