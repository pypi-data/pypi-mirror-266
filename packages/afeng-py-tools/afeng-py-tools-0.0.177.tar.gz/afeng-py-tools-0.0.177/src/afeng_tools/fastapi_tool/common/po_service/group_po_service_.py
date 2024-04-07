from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.fastapi_tool.common.service import icon_base_service
from afeng_tools.pydantic_tool.model.common_models import LinkItem


class GroupPoService(PoService):
    """
    使用示例：group_po_service = GroupPoService(app_info.db_code, GroupInfoPo)
    """
    _table_name_ = "tb_group_info"

    def get_group(self, title: str, group_code: str, type_code: str) -> Any:
        group_po = self.get(self.model_type.title == title,
                            self.model_type.code == group_code, self.model_type.type_code == type_code)
        if not group_po:
            group_po = self.save(self.model_type(
                title=title,
                code=group_code,
                type_code=type_code
            ), auto_code=True)
        return group_po

    def get_by_code(self, group_code: str) -> Any:
        return self.get(self.model_type.code == group_code)

    @classmethod
    def convert_to_link_item(cls, group_po, is_active: bool = False, group_href_prefix: str = '/category') -> LinkItem:
        return LinkItem(
            title=group_po.title,
            href=f'{group_href_prefix}/{group_po.code}',
            code=group_po.code,
            description=group_po.description,
            image=icon_base_service.get_icon_code(icon_type=group_po.icon_type,
                                                  icon_value=group_po.icon_value,
                                                  alt=group_po.title,
                                                  image_src=group_po.image_src),
            is_active=is_active)
