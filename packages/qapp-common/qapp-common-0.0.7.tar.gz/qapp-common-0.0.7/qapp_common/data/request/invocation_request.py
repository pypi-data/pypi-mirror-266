"""
    QApp Platform Project invocation_request.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..callback.callback_url import CallbackUrl
from ..request.request import Request
from ...enum.processing_unit import ProcessingUnit


class InvocationRequest(Request):
    def __init__(self, request_data: dict):
        super().__init__(request_data)
        self.input = request_data.get("input")
        self.shots = request_data.get("shots")
        self.device_id = request_data.get("deviceId")
        self.device_selection_url = request_data.get("serverUrl")
        self.sdk = request_data.get("sdk").lower() if request_data.get("sdk") else None
        self.circuit_export_url = request_data.get("circuitExportUrl")
        self.processing_unit = (
            ProcessingUnit.GPU
            if ProcessingUnit.GPU.value.__eq__(request_data.get("processingUnit"))
            else ProcessingUnit.CPU
        )
        self.preparation = CallbackUrl(request_data.get("preparation"))
