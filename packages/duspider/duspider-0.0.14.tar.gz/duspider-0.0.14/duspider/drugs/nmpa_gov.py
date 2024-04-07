# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/23 10:19
# see https://www.nmpa.gov.cn/datasearch/home-index.html#category=yp
import logging
import time
from math import ceil
from pathlib import Path

import execjs
from fake_useragent import UserAgent
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from duspider.base import Spider

logger = logging.getLogger("duspider.drugs.nmapgov")


class NmapGov(Spider):
    """国家药监局 数据采集程序
        sign: 签名破解
        see https://www.nmpa.gov.cn/datasearch/home-index.html#category=yp
    """

    def __init__(self, max_retry=5, sem=15, js_file=Path('NmapGov.js'), js_func='jsonMD5ToStr', **kwargs):
        super().__init__(max_retry=max_retry, sem=sem, **kwargs)
        self.js_func = js_func
        self.js_file = js_file
        self.js = execjs.compile(self.js_from_file(js_file))
        self.search_url = 'https://www.nmpa.gov.cn/datasearch/data/nmpadata/search'
        self.conf_url = 'https://www.nmpa.gov.cn/datasearch/config/{}.json?date={}'
        self.detail_url = 'https://www.nmpa.gov.cn/datasearch/data/nmpadata/queryDetail'
        self.last = ''
        self.item = {
            "国产": "ff80808183cad75001840881f848179f",  # 国产药品
            "进口": "ff80808183cad7500184088665711800",  # 进口药品
        }

    def get_ua(self):
        ua = UserAgent()
        while True:
            ua_ = ua.random
            if 'MSIE' not in str(ua_) and ua_ != self.last:
                self.last = ua_
                return ua_

    async def get_conf(self, item_id):
        item = {}
        date_ = self.new_time()
        conf_url = self.conf_url.format(item_id, date_)
        resp = await self.get(conf_url)
        if resp.status_code == 200:
            detail_feild = resp.json()['detailFeild']
            for row in detail_feild:
                alias = row['alias']
                desc = row['desc']
                item[alias] = desc
        return item

    def new_headers(self, params, timestamp):
        """创建请求headers"""
        params_str = self.params_to_str(params)
        self.headers['sign'] = self.get_sign(params_str)
        self.headers['timestamp'] = str(timestamp)
        self.headers['User-Agent'] = self.get_ua()
        return self.headers

    @staticmethod
    def params_to_str(params_dic):
        _temp = []
        items = sorted(params_dic.items(), key=lambda item: item[0])
        for (k, v) in items:
            _temp.append(f'{k}={v}')
        return '&'.join(_temp)

    @staticmethod
    def js_from_file(file_name):
        """读取js文件"""
        with open(file_name, encoding='UTF-8') as f:
            logger.debug(f'加载 加密js文件[{file_name}]')
            return f.read()

    def new_time(self):
        return int(time.time() * 1000)

    def new_params(self, item_id, page=1, search_value='*'):
        return {
            'isSenior': 'N',
            'itemId': item_id,
            'pageNum': page,
            'pageSize': 20,
            'searchValue': search_value,
            'timestamp': self.new_time(),
        }

    def new_info_params(self, id_, item_id):
        return {
            'id': id_,  # 药品id
            'itemId': item_id,  # self.item
            'timestamp': self.new_time(),
        }

    def get_sign(self, params_str):
        """签名 sign"""
        return self.js.call(self.js_func, params_str)

    async def run(self):
        async for row in tqdm_asyncio(self.all(item_id='进口'), desc='进口'):
            print(row)

    async def all(self, params=None, item_id='国产'):
        if not params:
            params = self.new_params(item_id=self.item[item_id])

        timestamp = params['timestamp'] or self.new_time()
        headers = self.new_headers(params, timestamp)
        conf_data = await self.get_conf(self.item[item_id])
        resp = await self.get(self.search_url, params=params, headers=headers)

        if resp.status_code == 200:
            js_data = resp.json()
            total = js_data['data']['total']
            pages = ceil(total / 20) + 1
            async for row in self.page_list(js_data['data']['list'], item_id, conf_data):
                yield row
            for page in tqdm(range(2, pages), desc='翻页'):
                params = self.new_params(item_id=self.item[item_id], page=page)
                timestamp = params['timestamp']
                headers = self.new_headers(params, timestamp)

                resp = await self.get(self.search_url, params=params, headers=headers)
                if resp.status_code == 200:
                    js_data = resp.json()
                    async for row in self.page_list(js_data['data']['list'], item_id, conf_data):
                        yield row

    @staticmethod
    async def parse_data(data, conf_data):
        item = {}
        for k, v in data.items():
            item[k] = {'desc': conf_data.get(k), 'value': v}
        return item

    async def page_list(self, data, item_id, conf_data):
        for row in data:
            id_ = row.get('f4') or row.get('f3')

            params = self.new_info_params(item_id=self.item[item_id], id_=id_)
            timestamp = params['timestamp']
            headers = self.new_headers(params, timestamp)
            resp = await self.get(self.detail_url, params=params, headers=headers)
            if resp.status_code == 200:
                yield await self.parse_data(resp.json()['data']['detail'], conf_data)


if __name__ == '__main__':
    gov = NmapGov(max_retry=3, sem=15)
    import asyncio

    asyncio.run(gov.run())
