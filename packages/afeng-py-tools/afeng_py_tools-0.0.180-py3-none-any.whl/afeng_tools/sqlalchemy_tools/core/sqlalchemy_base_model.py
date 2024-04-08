from afeng_tools.sqlalchemy_tools import sqlalchemy_settings


def get_base_model(db_code: str = 'default') -> type:
    """获取基础Model"""
    return sqlalchemy_settings.get_database(db_code).BaseModel


def is_model_instance(model_instance) -> bool:
    """是否是Model的实例"""
    if model_instance and not isinstance(model_instance, str) and not isinstance(model_instance, int) and not isinstance(model_instance, float) and not isinstance(model_instance, tuple) and not isinstance(model_instance, list) and not isinstance(model_instance, dict):
        return '_sa_instance_state' in model_instance.__dict__
    return False


def is_model_class(model_class: type) -> bool:
    """是否是Model的子类"""
    if model_class:
        return '__table__' in model_class.__dict__
    return False
