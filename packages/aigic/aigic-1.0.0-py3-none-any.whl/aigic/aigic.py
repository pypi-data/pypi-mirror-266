import http.client
import json
import base64
from typing import (Optional,Dict,Any)
from enum import Enum

class AuthType(Enum):
    API = 1
    JWT = 2
    NONE = 3


default_path = {AuthType.API: "/api", AuthType.JWT: "/jwt"}


class AIGIC:
    def __init__(self,
                 auth:str,
                 host:str = None,
                 headers:Optional[Dict[str,Any]] = None) -> None:
        super().__init__()

        if auth is None or auth == "":
            raise Exception("auth is not found")

        self.auth = auth
        self.host = host
        self.auth_type = AuthType.NONE
        self.base_path = ""
        self.headers = headers
        self.parse()

    def parse(self):
        api_version = '/v1'
        if self.headers is not None and api_version in self.headers:
            api_version = self.headers.get(api_version)

        self.auth_type = self.parse_auth_type()
        self.base_path = default_path[self.auth_type] + api_version

    def parse_auth_type(self) -> AuthType:
        decoded_bytes = base64.b64decode(self.auth)
        decoded_string = decoded_bytes.decode('utf-8',errors='ignore')
        if "JWT" in decoded_string:
            return AuthType.JWT
        return AuthType.API

    def prediction(self,
                   api_path:str,
                   input:Optional[Dict[str,Any]] = None):
        host = self.host
        if host is None or host == "":
            host = "api.aigic.ai"
        auth = self.auth
        api_url = self.base_path + api_path

        conn = http.client.HTTPSConnection(host)

        data = {
            "input": input
        }

        payload = json.dumps(data)

        headers = (self.headers or {})
        if self.auth_type == AuthType.JWT:
            headers['Authorization'] = 'Bearer ' + auth
        elif self.auth_type == AuthType.API:
            headers['apikey'] = auth

        conn.request("POST", api_url, payload, headers)

        res = conn.getresponse()
        data = res.read()
        result = json.loads(data.decode("utf-8"))

        conn.close()

        # print(data.decode("utf-8"))

        return result
