from typing import Any

from afeng_tools.fastapi_tool.common.po_service.category_po_service_ import CategoryPoService
from afeng_tools.fastapi_tool.common.service.base_service import BaseService
from afeng_tools.pydantic_tool.model.common_models import LinkItem


class CategoryService(BaseService):
    """
    使用示例：category_service = CategoryService(app_info.db_code, CategoryInfoPo)
    """

    po_service_type = CategoryPoService

    def _up_tree_category(self, category_code: int, category_dict: dict[int, Any],
                          recursion: bool = True,
                          include_root: bool = True) -> list[Any]:
        """向上获取递归获取分类信息"""
        category_list = []
        tmp_category = category_dict.get(category_code)
        if tmp_category:
            if include_root:
                category_list.append(tmp_category)
            if tmp_category.parent_code:
                parent_category = category_dict.get(tmp_category.parent_code)
                if parent_category:
                    category_list.append(parent_category)
                    if recursion:
                        category_list.extend(
                            self._up_tree_category(parent_category.parent_code, category_dict, recursion=recursion,
                                                   include_root=True))
        category_list.reverse()
        return category_list

    def _down_tree_category(self, category_code: int, category_dict: dict[int, Any],
                            recursion: bool = True,
                            include_root: bool = True) -> list[Any]:
        """
        向下获取递归获取分类信息， 第一项是当前分类
        :param category_code:
        :param category_dict:
        :param recursion: 是否层级递归
        :return:
        """
        category_list = []
        tmp_category = category_dict.get(category_code)
        if tmp_category:
            if include_root:
                category_list.append(tmp_category)
            for tmp_po in sorted(category_dict.values(), key=lambda x: x.order_num, reverse=True):
                if tmp_po.parent_code == category_code:
                    category_list.append(tmp_po)
                    if recursion:
                        category_list.extend(self._down_tree_category(tmp_po.code, category_dict,
                                                                      recursion=recursion,
                                                                      include_root=False))
        return category_list

    def get_category_list(self, category_code: int, group_code: int = None, category_dict: dict[int, Any] = None,
                          recursion: bool = True,
                          up: bool = True,
                          include_root: bool = True) -> list[Any]:
        """
        通过分类编码获取分类列表: 如：['程序开发','Java','Java虚拟机']
        :param category_code:
        :param group_code: 分组编码
        :param category_dict:
        :param recursion: 是否递归，True: 递归获取； False: 只获取父级或子集
        :param up:
            当为True时，向上获取，如当前是Java虚拟机,获取到的是['程序开发','Java','Java虚拟机']
            当为False时，向下获取，如当前是Java,获取到的是['Java基础','Java安全','Java虚拟机', ,'JavaWeb开发']
        :param include_root:
        :return: 分类列表
        """
        if group_code is None:
            category_info = self.po_service.get_one(self.po_model_type.code == category_code)
            group_code = category_info.group_code
        if category_dict is None:
            category_dict = {tmp.code: tmp for tmp in self.po_service.query_group_data(group_code)}
        return self._up_tree_category(category_code, category_dict,
                                      recursion=recursion,
                                      include_root=include_root) if up else self._down_tree_category(category_code,
                                                                                                     category_dict,
                                                                                                     recursion=recursion,
                                                                                                     include_root=include_root)

    def get_up_category_title_list(self, category_code: int, group_code: int = None) -> list[str]:
        """获取向上的分类标题"""
        category_list = self.get_category_list(group_code=group_code, category_code=category_code,
                                               recursion=True, up=True)
        return [tmp.title for tmp in category_list]

    def get_category_link_list(self, group_code: str, parent_code: str = None,
                               category_dict: dict[str, Any] = None,
                               is_recursion: bool = False) -> list[LinkItem]:
        """获取分类链接列表"""
        result_list = []
        if category_dict is None:
            category_dict = {tmp.code: tmp for tmp in self.po_service.query_group_data(group_code) if tmp.is_enable}
        for tmp_category in sorted([tmp for tmp in category_dict.values() if tmp.parent_code == parent_code],
                                   key=lambda x: x.order_num, reverse=True):
            tmp_link_item = self.po_service.convert_to_link_item(tmp_category)
            if is_recursion:
                tmp_link_item.children = self.get_category_link_list(group_code=group_code,
                                                                     parent_code=tmp_category.code,
                                                                     category_dict=category_dict,
                                                                     is_recursion=is_recursion)
            result_list.append(tmp_link_item)
        return result_list
