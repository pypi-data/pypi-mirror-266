from typing import Any

from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService
from afeng_tools.fastapi_tool.common.service import icon_base_service
from afeng_tools.pydantic_tool.model.common_models import LinkItem


class ArticlePoService(PoService):
    """
    使用示例：article_po_service = ArticlePoService(app_info.db_code, ArticleInfoPo)
    """
    _table_name_ = "tb_article_info"

    def get_by_code(self, type_code: str, article_code: str) -> Any:
        return self.get(self.model_type.type_code == type_code, self.model_type.code == article_code)

    @classmethod
    def convert_to_link_item(cls, article_po, is_active: bool = False, article_href_prefix: str = '/article') -> LinkItem:
        return LinkItem(
            title=article_po.title,
            href=f'{article_href_prefix}/{article_po.type_code}/{article_po.code}',
            code=article_po.code,
            description=article_po.description,
            image=icon_base_service.get_icon_code(icon_type=article_po.icon_type,
                                                  icon_value=article_po.icon_value,
                                                  alt=article_po.title,
                                                  image_src=article_po.image_src),
            is_active=is_active)
