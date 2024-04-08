# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : client.py
# @Time     : 2023/11/29 12:35
from urllib import parse as urllib_parse

from fastapi import HTTPException, APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

SESSION_KEY = 'fastapix-user'


class BaseClient:

    def __init__(
            self,
            endpoint: str,
            **kwargs
    ):
        """

        :param endpoint: SSO 认证服务
        :param client_id:
        :param client_secret:
        :param certificate:
        :param org_name:
        :param application_name:
        :param session_secret_type:
        :param session_secret_key:
        """
        self.endpoint = endpoint

    @staticmethod
    def authenticate_user(request: Request):
        try:
            user = request.session.get(SESSION_KEY, None)
            if user:
                return user
            else:
                raise HTTPException(status_code=401, detail='Unauthorized')
        except BaseException as _:
            raise HTTPException(status_code=401, detail='Unauthorized')

    def router(
            self,
            prefix='/sso',
            tags=None
    ) -> APIRouter:
        if tags is None:
            tags = ['SSO']
        router = APIRouter(prefix=prefix, tags=tags)

        signin_path: str = '/signin'
        signout_path: str = '/signout'

        @router.get(signin_path, include_in_schema=False)
        @router.post(signin_path, include_in_schema=False)
        async def signin(request: Request, redirect_url: str = Query("/docs")):
            user = await self.verify_user(request)
            request.session[SESSION_KEY] = user
            return RedirectResponse(redirect_url)

        @router.get(signout_path, include_in_schema=False)
        @router.post(signout_path, include_in_schema=False)
        async def signout(request: Request, redirect_url: str = Query("/docs")):
            request.session.pop(SESSION_KEY)
            return RedirectResponse(redirect_url)

        @router.get('/toLogin')
        async def to_login(request: Request, redirect_url: str = Query("/docs")):
            parent_url = str(request.url).split('/toLogin')[0]
            query = urllib_parse.urlencode({'redirect_url': redirect_url})
            signin_url = parent_url + signin_path + '?' + query
            return RedirectResponse(await self.sso_login_url(signin_url))

        @router.get('/toLogout')
        async def to_logout(request: Request, redirect_url: str = Query("/docs")):
            parent_url = str(request.url).split('/toLogout')[0]
            query = urllib_parse.urlencode({'redirect_url': redirect_url})
            signout_url = parent_url + signin_path + '?' + query
            return RedirectResponse(await self.sso_logout_url(signout_url))

        return router

    async def sso_login_url(self, signin_url: str) -> str:
        raise NotImplementedError

    async def sso_logout_url(self, signout_url: str) -> str:
        raise NotImplementedError

    async def verify_user(self, request: Request) -> dict:
        raise NotImplementedError
