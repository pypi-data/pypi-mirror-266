from afeng_tools.fastapi_tool.common.po_service.link_po_service_ import LinkPoService
from afeng_tools.fastapi_tool.common.service.base_service import BaseService


class LinkService(BaseService):
    """
    使用示例：link_service = LinkService(app_info.db_code, LinkInfoPo)
    """

    po_service_type = LinkPoService
    pass
