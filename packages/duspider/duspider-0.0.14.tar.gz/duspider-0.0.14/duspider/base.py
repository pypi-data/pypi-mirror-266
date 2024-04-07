# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/9/18 9:42
import time

import httpx
from httpx import Response

from duspider.exceptions import RequestError
from duspider.tools import get_ua


class Spider:
    def __init__(self, timeout=30, max_retry=10, sem=15, headers=None, cookies=None):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
        }
        self.cookies = cookies
        self.timeout = timeout
        self.max_retry = max_retry  # 最多重试次数
        # max_keepalive_connections 允许的保持活动状态连接数，或None始终允许。（默认值 20）
        # max_connections 允许的最大连接数，或None无限制。（默认值 100）
        limits = httpx.Limits(max_keepalive_connections=sem, max_connections=sem + 3)
        # client = httpx.Client(limits=limits) # 同步
        self.client = httpx.AsyncClient(cookies=cookies, headers=headers, limits=limits)  # 异步

    def get_headers(self, headers=None):
        if headers:
            headers['user-agent'] = get_ua()
            return headers
        elif self.headers:
            self.headers['user-agent'] = get_ua()
            return self.headers
        return {'user-agent': get_ua()}

    async def post(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = await self.client.post(url,
                                              timeout=self.timeout,
                                              follow_redirects=True,
                                              **kwargs)
                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''

    async def get(self, url, **kwargs) -> Response:
        for i in range(self.max_retry):
            try:
                resp = await self.client.get(url,
                                             timeout=self.timeout,
                                             follow_redirects=True,
                                             **kwargs)

                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''


HEADERS = {
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76',
}
