from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.pydantic_tool.model.common_models import LinkItem


class TagPoService(PoService):
    """
    使用示例：tag_po_service = TagPoService(app_info.db_code, TagInfoPo)
    """
    _table_name_ = "tb_tag_info"

    def get_by_code(self, type_code: str, code: str) -> Any:
        return self.get(self.model_type.type_code == type_code, self.model_type.code == code)

    @classmethod
    def convert_to_link_item(cls, tag_po, is_active: bool = False, tag_href_prefix: str = '/tag') -> LinkItem:
        return LinkItem(
            title=tag_po.title,
            href=f'{tag_href_prefix}/{tag_po.code}',
            code=tag_po.code,
            description=tag_po.description,
            is_active=is_active)

