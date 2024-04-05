from typing import Any, TypeVar, Generic, Callable

from afeng_tools.id_code_tool import id_code_tools
from afeng_tools.sqlalchemy_tools import sqlalchemy_settings
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_enums import SortTypeEnum
from afeng_tools.sqlalchemy_tools.crdu import base_crdu
from sqlalchemy.orm import Query

ModelType = TypeVar('ModelType', bound=Any)


class PoService(Generic[ModelType]):
    # 表名
    _table_name_: str = None

    def __init__(self, db_code: str, model_type: type = None):
        self.db_code = db_code
        self.Base = sqlalchemy_settings.get_database(db_code).Base
        if model_type is not None:
            self.model_type = model_type
        if hasattr(self, 'model_type') and self.model_type is None and self._table_name_:
            self.model_type = self._get_model_type()
        elif self._table_name_:
            self.model_type = self._get_model_type()

    def _get_model_type(self):
        model_type_list = [tmp_mapper.entity for tmp_mapper in self.Base.registry.mappers if
                           tmp_mapper.local_table.name == self._table_name_]
        if model_type_list:
            return model_type_list[0]

    def __class_getitem__(cls, item):
        if '__table__' in item.__dict__:
            cls.model_type = item
        return super().__class_getitem__(item)

    def add(self, po: ModelType) -> ModelType:
        return base_crdu.add(po, db_code=self.db_code)

    def add_batch(self, model_list: list[ModelType]) -> list[ModelType]:
        return base_crdu.add_all(model_list, db_code=self.db_code)

    def update(self, po: ModelType, *criterion) -> ModelType:
        return base_crdu.update(po, *criterion, db_code=self.db_code)

    def update_batch(self, model_list: list[ModelType]) -> list[ModelType]:
        return base_crdu.update_batch(model_list, db_code=self.db_code)

    def save(self, po: ModelType, *criterion, auto_code: bool = False) -> ModelType:
        po = base_crdu.save(po, *criterion, db_code=self.db_code)
        if auto_code:
            if po.code is None:
                po.code = id_code_tools.get_code_by_id(po.id)
                po = base_crdu.update(po, db_code=self.db_code)
        return po

    def save_batch(self, model_list: list[ModelType], criterion_fun: Callable, exist_update: bool = True) -> list[ModelType]:
        """
        批量保存
        :param model_list:  Model数据列表
        :param criterion_fun: 通过接受model，返回判断条件, 如：lambda x: type(x).ts_code == x.ts_code
        :param exist_update: 如果存在则更新，如果为False，则如果存在则啥也不做
        :return: Model数据列表
        """
        return base_crdu.save_batch_by_where(model_list, criterion_fun, exist_update=exist_update, db_code=self.db_code)

    def delete(self, *criterion):
        return base_crdu.delete(self.model_type, *criterion, db_code=self.db_code)

    def create_query(self, *criterion) -> Query:
        return base_crdu.create_query(self.model_type, *criterion, db_code=self.db_code)

    def get(self, *criterion) -> ModelType:
        return base_crdu.query_one(self.model_type, *criterion, db_code=self.db_code)

    def query_more(self, *criterion, sort_column: str = 'order_num',
                   sort_type: SortTypeEnum = SortTypeEnum.desc) -> list[ModelType]:
        return base_crdu.query_all(self.model_type, *criterion, sort_column=sort_column, sort_type=sort_type,
                                   db_code=self.db_code)

    def query_page(self, page_num: int, page_size: int, *criterion,
                   sort_column: str = 'order_num', sort_type: SortTypeEnum = SortTypeEnum.desc) -> list[ModelType]:
        return base_crdu.query_page(self.model_type, page_num, page_size, *criterion,
                                    sort_column=sort_column, sort_type=sort_type,
                                    db_code=self.db_code)

    def count(self, *criterion) -> int:
        return base_crdu.count(self.model_type, *criterion, db_code=self.db_code)
