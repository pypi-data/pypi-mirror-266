# -*- coding: utf-8 -*-
# @project: SPIDERS
# @Author：dyz
# @date：2023/9/15 10:25
# Uniprot
import logging
import re

from requests import Session
import httpx

from duspider.base import HEADERS

logger = logging.getLogger("duspider.uniprot")


class Uniprot:

    def __init__(self, max_retry=3, **kwargs):
        self.max_retry = max_retry  # 一个连接的最大重试次数
        self.sess = Session()
        self.timeout = 0.1
        self.sess = httpx.AsyncClient(headers=HEADERS)
        self.fields = "accession, reviewed, id, protein_name, gene_names, organism_name, length, mass"
        self.query = "(*)"
        # self.query = "(*) AND(model_organism: 9606)"
        self.searchUrl = 'https://rest.uniprot.org/uniprotkb/search'
        # self.entryUrl = 'https://www.uniprot.org/uniprotkb/A0A1B0GTW7/entry'
        self.entryUrl = 'https://rest.uniprot.org/uniprotkb/A0A1B0GTW7'
        self.Model = 'model_organism'
        self.Human = '9606'
        self.Rice = '39947'
        self.ThaLiana = '3702'
        self.Rat = '10116'
        self.Mouse = '10090'
        for k, v in kwargs:
            setattr(self, k, v)

    async def request(self, med, url, timeout=300, **kwargs):
        for i in range(self.max_retry):
            try:
                res = await self.sess.request(med, url, timeout=timeout or self.timeout, **kwargs)
                return res
            except httpx.RequestError as exc:
                logger.error(exc)
            except httpx.HTTPError as exc:
                logger.error(exc)
        return None

    async def human(self, query='(*)', fields='', size=25):
        query = query + f' AND ({self.Model}:{self.Human})'
        async for data in self.all(query, fields, size):
            yield data
        return

    async def rice(self, query='(*)', fields='', size=25):
        query = query + f' AND ({self.Model}:{self.Rice})'
        async for data in self.all(query, fields, size):
            yield data
        return

    async def tha_liana(self, query='(*)', fields='', size=25):
        query = query + f' AND ({self.Model}:{self.ThaLiana})'
        async for data in self.all(query, fields, size):
            yield data
        return

    async def rat(self, query='(*)', fields='', size=25):
        query = query + f' AND ({self.Model}:{self.Rat})'
        async for data in self.all(query, fields, size):
            yield data
        return

    async def mouse(self, query='(*)', fields='', size=25):
        query = query + f' AND ({self.Model}:{self.Mouse})'
        async for data in self.all(query, fields, size):
            yield data
        return

    async def all(self, query='(*)', fields='', size=25, timeout=300):
        """
        获取所有数据列表
        :param query:
        :param fields:
        :param size:
        :param timeout:
        :return:
        """
        query = query or self.query
        fields = fields or self.fields
        while True:
            params = {"query": query, "fields": fields, "size": size}
            response = await self.request('get', self.searchUrl, params=params, timeout=timeout)
            link = response.headers.get('Link', '')
            yield response.json()['results']
            cursor = re.findall('&cursor=(.*?)&size=', link)[0]
            params['cursor'] = cursor
            if not link:
                return

    def parse_html(self, html):
        """
        解析网页
        :param html:
        :return:
        """
        pass

    def parse(self, html):
        """数据解析"""
        pass

    async def run(self):
        async for data in self.all():
            print(data)


if __name__ == '__main__':
    uni = Uniprot()
    import asyncio

    asyncio.run(uni.run())
