from typing import List

from ..models import APIRequest
from ...util import (
    serialize_multi_instance,
    serialize_semi_colon_separated,
)


class BaseController:

    CONTROLLER = None
    SEMI_COLON_PARAMS = ["selected_fields", "annotations"]
    MULTI_INSTANCE_PARAMS = {
        "web_id": "webId",
        "times": "time",
        "paths": "path"
    }

    def __init__(
        self,
        method: str = None,
        protocol: str = None,
        webid: str = None,
        action: str = None,
        add_path: List[str] = None,
        **kwargs
    ) -> None:

        assert self.CONTROLLER is not None

        self.method = method
        self.protocol = protocol
        self.webid = webid
        self.action = action
        self.add_path=add_path
        self.params = kwargs
        self._serialize_special_params()
    
    def build_request(self, **kwargs):
        """Return an instance of APIRequest"""
        kwargs.update(self.params)
        return APIRequest(
            method=self.method,
            protocol=self.protocol,
            controller=self.CONTROLLER,
            webid=self.webid,
            action=self.action,
            add_path=self.add_path,
            **kwargs
        )
    
    def _serialize_special_params(self):
        """Serialize semi colon separated and multi instance params"""
        for validate in self.SEMI_COLON_PARAMS:
            param = self.params.get(validate)
            if param is not None:
                serialized = serialize_semi_colon_separated(param)
                self.params.update({validate: serialized})
        for validate, key in self.MULTI_INSTANCE_PARAMS.items():
            param = self.params.get(validate)
            if param is not None:
                serialized = serialize_multi_instance(key, param)
                self.params.pop(validate)
                self.params.update({key: serialized})
