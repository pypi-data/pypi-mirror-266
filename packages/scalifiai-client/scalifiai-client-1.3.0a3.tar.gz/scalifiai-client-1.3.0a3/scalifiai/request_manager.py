import os
from requests import request

from .constants import (
    CREDENTIALS_AUTH_METHOD_API_KEY_KEY,
    AUTH_API_KEY_HEADER_NAME,
    REQUEST_NAMAGER_VERIFY_SSL_NAME,
    REQUEST_NAMAGER_ALLOW_RESPONSE_REDIRECTS_NAME,
)
from .exceptions import NotImplementedException


class RequestManager:
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    def __init__(self, *, credential_manager=None) -> None:
        self.credential_manager = credential_manager

    def add_request_auth(self, *, headers=None):

        if self.credential_manager.method == CREDENTIALS_AUTH_METHOD_API_KEY_KEY:
            headers = {
                **headers,
                AUTH_API_KEY_HEADER_NAME: self.credential_manager.api_key,
            }
        else:
            raise NotImplementedException(
                extra_info=f"Invalid credential manager method: {self.credential_manager.method}"
            )

        return headers

    def send_request(
        self,
        *,
        method=None,
        url=None,
        query_params=None,
        data=None,
        headers=None,
        files=None,
        stream=None,
    ):

        if headers == None:
            headers = {}

        headers = self.add_request_auth(headers=headers)

        # TODO[VIMPORTANT] ADD CODE HERE TO HANDLE GENERIC ERRORS LIKE SUBSCRIPTION BASED, THROTTLING BASED, AUTHENTICATION, AUTHORIZATION AND BACKEND ERROR, REST CAN BE HANDLED EVERYWHERE ELSE

        return request(
            method=method,
            url=url,
            params=query_params,
            json=data,
            headers=headers,
            files=files,
            stream=stream,
            verify=bool(int(os.environ.get(REQUEST_NAMAGER_VERIFY_SSL_NAME, "1"))),
            allow_redirects=bool(
                int(os.environ.get(REQUEST_NAMAGER_ALLOW_RESPONSE_REDIRECTS_NAME, "0"))
            ),
        )
