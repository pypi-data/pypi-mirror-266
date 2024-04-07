"""
导入工具
"""
import importlib
import threading


def import_jinja2():
    try:
        import jinja2
        return jinja2
    except ModuleNotFoundError:
        jinja2 = None
    return jinja2


def import_module_by_name(module_name: str):
    """通过名称导入模块"""
    return importlib.import_module(module_name)


def import_class(class_full_name: str):
    """
    导入类，示例：ErrorService = import_class('demo.class_demo.ErrorService')
                error_service = ErrorService()
    :param class_full_name: 'demo.class_demo.ErrorService'
    :return:
    """
    _module_name, _class_name = class_full_name.rsplit('.', maxsplit=1)
    # 动态导入模块
    tmp_module = importlib.import_module(_module_name)
    # 从模块中获取类
    return getattr(tmp_module, _class_name)


# 创建一个互斥锁对象
import_lock = threading.Lock()


def import_module_thread_safe(module_name):
    # 获取锁对象
    lock = import_lock.acquire()
    try:
        # 导入模块
        module = importlib.import_module(module_name)
    finally:
        # 释放锁对象
        import_lock.release()
    return module
