"""
    QApp Platform Project job_fetching_request.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from .request import Request


class JobFetchingRequest(Request):
    def __init__(self, request_data):
        super().__init__(request_data)
        self.provider_authentication = request_data.get("providerAuthentication")
