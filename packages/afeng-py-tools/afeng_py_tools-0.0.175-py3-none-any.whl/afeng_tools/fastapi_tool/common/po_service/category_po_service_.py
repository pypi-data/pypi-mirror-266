from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.fastapi_tool.common.service import icon_base_service
from afeng_tools.pydantic_tool.model.common_models import LinkItem
from afeng_tools.sqlalchemy_tools.crdu import base_crdu


class CategoryPoService(PoService):
    """
    使用示例：category_po_service = CategoryPoService(app_info.db_code, CategoryInfoPo)
    """
    _table_name_ = "tb_category_info"

    def get_category(self, title: str, group_code: int, parent_code: int = None) -> Any:
        category_po = self.get(self.model_type.title == title,
                               self.model_type.group_code == group_code, self.model_type.parent_code == parent_code)
        if not category_po:
            category_po = self.save(self.model_type(
                group_code=group_code,
                parent_code=parent_code,
                title=title
            ), auto_code=True)
        return category_po

    def query_all_data(self, group_code: int = None) -> list:
        """查询所有数据"""
        if group_code:
            return base_crdu.query_all(self.model_type, self.model_type.group_code == group_code, db_code=self.db_code)
        else:
            return base_crdu.query_all(self.model_type, db_code=self.db_code)

    def query_all_data_dict(self, group_code: int = None) -> dict[str, Any]:
        """
        查询所有数据字典(code为键)
        :return: {code: BookCategoryPo}
        """
        return {tmp.code: tmp for tmp in self.query_all_data(group_code)}

    def query_group_data_dict(self) -> dict[str, list[Any]]:
        """
        查询分组数据字典(group_code为键)
        :return: {group_code: BookCategoryPo}
        """
        data_list = self.query_all_data()
        result_dict = dict()
        for tmp in data_list:
            if not result_dict.get(tmp.group_code):
                result_dict[tmp.group_code] = []
            result_dict[tmp.group_code].append(tmp)
        return result_dict

    def query_group_data(self, group_code: int,
                         category_dict: dict[int, list[Any]] = None) -> list[Any]:
        """
        查询某个分组的类别数据
        :param group_code: 分组编码
        :param category_dict: 类别字典：{group_code: BookCategoryPo}
        :return:
        """
        if category_dict:
            return category_dict.get(group_code)
        else:
            return base_crdu.query_all(self.model_type, self.model_type.group_code == group_code,
                                       db_code=self.db_code)

    def get_by_code(self, group_code: str, code: str) -> Any:
        return self.get(self.model_type.group_code == group_code, self.model_type.code == code)

    @classmethod
    def convert_to_link_item(cls, category_po, is_active: bool = False,
                             category_href_prefix: str = '/category') -> LinkItem:
        return LinkItem(
            title=category_po.title,
            href=f'{category_href_prefix}/{category_po.code}',
            code=category_po.code,
            description=category_po.description,
            image=icon_base_service.get_icon_code(icon_type=category_po.icon_type,
                                                  icon_value=category_po.icon_value,
                                                  alt=category_po.title,
                                                  image_src=category_po.image_src),
            is_active=is_active
        )
