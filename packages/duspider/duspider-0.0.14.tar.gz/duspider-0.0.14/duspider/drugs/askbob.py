# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/28 10:37
# see https://www.jk.cn/ab-special/#/
import logging

from pydantic import BaseModel
from duspider.base import HEADERS, Spider

from typing import List
from pydantic import BaseModel

from duspider.tools import make_md5

logger = logging.getLogger("duspider.drugs.askbob")


class AskBobHit(BaseModel):
    uid: str
    name: str
    html: str
    url: str


class AskBob(Spider):
    """AskBob 药品"""

    def __init__(self, headers, max_retry=3, **kwargs):
        super().__init__()
        self.headers = headers  # *必填需要登陆
        self.start_url = 'https://srv.jk.cn/ab-gateway/pedia/disease/dic'
        self.detail_url = 'https://srv.jk.cn/ab-gateway/pedia/disease/detail'
        self.params = {'type': 'X'}

    async def all(self):
        """所有一级数据列表"""
        params = {
            'dept': '',
            'name': '全部',
            'allSecondDept': 'true',
        }
        resp = await self.get(self.start_url, headers=self.headers, params=params)
        if resp.status_code == 200:
            data = resp.json()['data']
            for k, v in data.items():
                for i in v:
                    yield await self.detail(i['key'])

    async def detail(self, key) -> AskBobHit:
        params = {
            'key': key,
        }
        resp = await self.get(self.detail_url, params=params, headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()['data']
            name = data['title']
            return AskBobHit(html=data, uid=key, name=name)

    async def run(self):
        async for row in self.top1_list():
            print(row)

    async def parse(self):
        pass


if __name__ == '__main__':
    headers = {
        'authority': 'srv.jk.cn',
        'ab-client': 'PC',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'antibot': 'antibot:bWdNZk51Y1dRallJSVRuYQ==',
        'authentication': 'eyJhbGciOiJIUzUxMiJ9.eyJhcHBsaWNhdGlvbkFjY291bnRJbmZvIjp7ImlkIjozMjAwMzg2LCJjaGFubmVsSWQiOiIxMTAwNDkwMDAwIiwiaW5zdGl0dXRpb25JZCI6IjEyNDQ0NDAzMDAwMDMzMTAwMDAwMDAiLCJyb2xlIjoxLCJzb3VyY2UiOjAsInNlc3Npb25UeXBlIjoid2ViIiwiaXNBdXRvTG9naW4iOmZhbHNlLCJjb21tb25Vc2VySWQiOjM2OTE2MCwicGF5bWVudExldmVsIjowLCJhcGlVc2VySWQiOm51bGwsInJlYWxBdXRob3JpemF0aW9uIjpudWxsLCJ0b2tlblVwZGF0ZVRpbWUiOm51bGx9LCJleHAiOjE3MTU0MTEyNjh9.voZanOyoTQNZXsoJMCfWAzeljNdMQG5VkApQqIn6PI8NvnbdGzTHh3yXmgNqvQPSw2BX1B4rumKeDIc60bf83g',
        'cache-control': 'no-cache',
        'dnt': '1',
        'origin': 'https://www.jk.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jk.cn/',
        'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'uniqueequipmenttype': '3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    }
    s = AskBob(headers)
    import asyncio

    asyncio.run(s.run())
