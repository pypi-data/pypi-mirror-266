from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class BaseService:
    po_service_type: PoService = None

    def __init__(self, db_code: str, po_model_type: type = None, app_code: str = None):
        self.app_code = app_code
        self.db_code = db_code
        if po_model_type is not None:
            self.po_model_type = po_model_type
        if self.po_service_type:
            if po_model_type is not None:
                self.po_service = self.po_service_type(db_code=self.db_code, model_type=self.po_model_type)
            else:
                self.po_service = self.po_service_type(db_code=self.db_code)
            if not hasattr(self, 'po_model_type') or self.po_model_type is None:
                self.po_model_type = self.po_service.model_type
