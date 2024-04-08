# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _cas.py
# @Time     : 2023/11/29 13:24
from urllib import parse as urllib_parse

from cas import CASClient
from fastapi.requests import Request

from fastapix.sso._main import BaseClient


class CAS(BaseClient):

    def __init__(
            self,
            endpoint: str,
            *,
            version=3,
            **kwargs
    ):
        super().__init__(endpoint, **kwargs)
        import requests
        requests.packages.urllib3.disable_warnings()
        self.cas_client = CASClient(
            version=version,
            service_url=None,
            server_url=endpoint,
            verify_ssl_certificate=False
        )

    async def sso_login_url(self, signin_url: str) -> str:
        url = urllib_parse.urljoin(self.endpoint, 'login')
        query = urllib_parse.urlencode({'service': signin_url})
        return url + '?' + query

    async def sso_logout_url(self, signout_url: str) -> str:
        return self.cas_client.get_logout_url(signout_url)

    async def verify_user(self, request: Request) -> dict:
        ticket = request.query_params.get('ticket')
        _, attributes, _ = self.cas_client.verify_ticket(ticket)
        return attributes
