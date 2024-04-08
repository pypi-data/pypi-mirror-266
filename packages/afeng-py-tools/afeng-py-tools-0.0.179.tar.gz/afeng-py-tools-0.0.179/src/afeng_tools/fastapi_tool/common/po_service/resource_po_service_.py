from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class ResourcePoService(PoService):
    """
    使用示例：resource_po_service = ResourcePoService(app_info.db_code, ResourceInfoPo)
    """
    _table_name_ = "tb_resource_info"
    pass
