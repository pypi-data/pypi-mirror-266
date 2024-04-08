# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : casdoor.py
# @Time     : 2023/11/29 14:17
import requests
from casdoor import CasdoorSDK
from starlette.requests import Request

from fastapix.sso._main import BaseClient


class Casdoor(BaseClient):

    def __init__(
            self,
            endpoint: str,
            *,
            client_id: str,
            client_secret: str,
            certificate: str,

            org_name: str,
            application_name: str,
            **kwargs
    ):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        super().__init__(
            endpoint,
            **kwargs
        )
        self.sdk = CasdoorSDK(
            endpoint=endpoint,
            client_id=client_id,
            client_secret=client_secret,
            certificate=certificate,
            org_name=org_name,
            application_name=application_name,
            front_endpoint=endpoint
        )

    async def sso_login_url(self, signin_url: str) -> str:
        def get_auth_link(sdk, redirect_uri: str, response_type: str = "code", scope: str = "read"):
            url = sdk.front_endpoint + "/login/oauth/authorize"
            params = {
                "client_id": sdk.client_id,
                "response_type": response_type,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": sdk.application_name,
            }
            r = requests.request("post", url, params=params)
            return r.url

        return get_auth_link(self.sdk, redirect_uri=signin_url)

    async def sso_logout_url(self, signout_url: str) -> str:
        return signout_url

    async def verify_user(self, request: Request) -> dict:
        code = request.query_params.get("code")
        token = self.sdk.get_oauth_token(code).get("access_token")
        user = self.sdk.parse_jwt_token(token)
        return user
