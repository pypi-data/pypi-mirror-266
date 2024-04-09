from moesifapi.models import *
from datetime import datetime
from moesifapi.parse_body import ParseBody
import logging
import os

logger = logging.getLogger(__name__)

class EventMapper:

    def __init__(self):
        self.parse_body = ParseBody()

    @classmethod
    def get_headers(cls, headers):
        return {k: v for k, v in headers}

    @classmethod
    def get_utc_now(cls):
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    @classmethod
    def to_event(cls, event_request, event_response, user_id, company_id, session_token, metadata, blocked_by):
        # Prepare Event Model
        return EventModel(request=event_request,
                        response=event_response,
                        user_id=user_id,
                        company_id=company_id,
                        session_token=session_token,
                        metadata=metadata,
                        direction="Incoming",
                        blocked_by=blocked_by)

    async def to_request(self, request, log_body):
        request_time = self.get_utc_now()

        # convert headers (multiDictProxy class) into dict
        req_headers = self.get_headers(request.headers.items())

        req_body = None
        req_transfer_encoding = None
        if log_body:
            try:
                if request.body_exists:
                    request_text = await request.text()
                    req_body, req_transfer_encoding = self.parse_body.parse_string_body(request_text, None, req_headers)
            except Exception as e:
                pass

        # Prepare Event Request Model
        return EventRequestModel(time=request_time,
                                uri=str(request.url),
                                verb=request.method,
                                api_version=None,
                                ip_address=request.remote,
                                headers=req_headers,
                                body=req_body,
                                transfer_encoding=req_transfer_encoding)


    def to_response(self, response, log_body):
        
        response_time = self.get_utc_now()

        # convert headers (multiDictProxy class) into dict
        rsp_headers = self.get_headers(response.headers.items())

        rsp_body = None
        rsp_transfer_encoding = None

        if log_body:
            try:
                rsp_text = response.text
                rsp_body, rsp_transfer_encoding = self.parse_body.parse_string_body(rsp_text, None, rsp_headers)
            except Exception as e:
                pass

        return EventResponseModel(time=response_time,
                                status=response.status,
                                headers=rsp_headers,
                                body=rsp_body,
                                transfer_encoding=rsp_transfer_encoding)
