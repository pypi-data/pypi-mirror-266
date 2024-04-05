from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class SitemapPoService(PoService):
    """
    使用示例：sitemap_po_service = SitemapPoService(app_info.db_code, SitemapInfoPo)
    """
    _table_name_ = "tb_sitemap_info"
    pass
