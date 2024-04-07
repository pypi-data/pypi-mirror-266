# -*- coding: utf-8 -*-
# @Author：dyz
# @date：2023/11/22 10:29
import json
import logging
import random
import re
import time
from pathlib import Path
from typing import List

import requests
from playwright.async_api import async_playwright
from pydantic import BaseModel

from duspider.exceptions import RequestError
from duspider.medlive_login import MedLiveLogin, DownloadList

from duspider.tools import make_md5
from parsel import Selector
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

logger = logging.getLogger("duspider.guide.medlive")


class MaxRedirectsError(Exception):
    pass


class MedLiveGuide(MedLiveLogin):

    def __init__(self, context, auth, path, max_retry=3, timeout=20):
        super().__init__(context=context, auth=auth, path=path)
        self.start_url = 'https://guide.medlive.cn/guide/filter'
        self.url = 'https://guide.medlive.cn/more_publisher'
        self.guide_list_url = 'https://guide.medlive.cn/more_filter'
        self.new_guide_url = 'https://guide.medlive.cn/new_guide'
        self._token = ''
        self.cookies = None
        self.sess = None
        self.max_retry = max_retry
        self.timeout = timeout
        self.path = path
        self.zone = {
            # '0': "全部",
            '1': "中国",
            '2': "亚太",
            '3': "欧洲",
            '4': "北美",
            '5': "国际",
            '6': "其他",
        }
        self.types = {
            # "0": "全部",
            "1": "指南",
            "2": "解读",
            "3": "翻译",
        }
        self.category = {
            "7777": "内科",
            "8888": "外科",
            "9999": "其他",
        }
        self.sec = {'1': '心血管内科',
                    '2': '神经内科',
                    '3': '消化科',
                    '4': '肝病科',
                    '5': '内分泌科',
                    '6': '肿瘤科',
                    '7': '血液科',
                    '8': '神经科',
                    '9': '呼吸科',
                    '10': '肾内科',
                    '11': '风湿免疫科',
                    '12': '感染科',
                    '13': '普通外科',
                    '14': '神经外科',
                    '15': '胸心外科',
                    '16': '泌尿外科',
                    '17': '骨科',
                    '18': '整形外科',
                    '19': '麻醉科',
                    '20': '妇产科',
                    '21': '儿科',
                    '22': '眼科',
                    '23': '耳鼻咽喉科',
                    '24': '口腔科',
                    '25': '皮肤性病科',
                    '26': '急诊/重症',
                    '27': '影像科',
                    '28': '检验科',
                    '101': '全科医学',
                    '102': '药学',
                    '103': '病理',
                    '104': '营养学',
                    '105': '运动医学',
                    '106': '护理',
                    '107': '预防医学',
                    '108': '政府机构',
                    '109': '综合',
                    '999': '其他'}

    async def get(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = self.sess.get(url,
                                     timeout=self.timeout,
                                     **kwargs)
                # return await self.capt(url, resp)
                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    return ''
        return ''

    async def post(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = self.sess.post(url,
                                      timeout=self.timeout,
                                      **kwargs)

                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    return ''
        return ''

    async def capt(self, orgin_url, resp):
        """验证码"""
        if '您的访问过于频繁' in resp.text:
            logger.warning('您的访问过于频繁...')
            await self.save_capt()
            captcha = get_ocr(path)
            logger.debug(f'验证码：[{captcha}]')
            data = {
                'orginUrl': orgin_url,
                'captcha': captcha,
            }
            response = await self.post('https://drugs.medlive.cn/validCaptcha.do',
                                       cookies=cookies,
                                       headers=headers,
                                       data=data)
            return response
        return resp

    async def get_token(self):
        if not self.sess:
            self.sess = requests.Session()
        resp = await self.get(self.start_url)
        token_list = re.findall('_token: "(.*?)"', resp.text, flags=re.S)
        self._token = token_list[0]
        logger.debug(f'self._token: [{self._token}]')

    def get_params(self, uid, doc):
        down = doc.css('div.downLoad::attr(onclick)').get('').strip().replace('download_info("', "").rstrip('")')
        down = down.split('","')
        params = {
            "id": uid,
            "sub_type": "1",
            "fid": down[0],
            "fn": down[1],
            "sk": down[2],
        }
        return params

    def download(self, params, file):
        """下载"""
        try:
            resp = self.sess.get(url=self.download_url,
                                 cookies=self.cookies,
                                 params=params,
                                 headers=self.headers
                                 )
            print(resp, resp.history)
            if resp.headers['Content-Type'] != 'application/octet-stream':
                if '超过本日最大下载次数限制' in resp.text:
                    logger.warning('超过本日最大下载次数限制')
                    # print('超过本日最大下载次数限制')
                    raise MaxRedirectsError
                    # return '超过本日最大下载次数限制'
            # suffix = Path(params['fn']).suffix
            if not params['fn'].endswith('.pdf'):
                return False
            with open(file, 'wb') as f:
                f.write(resp.content)
            return file
        except Exception as e:
            logger.error(e)
            return False

    async def get_info(self, uid, item):
        resp = await self.get(item['url'])
        doc = Selector(resp.text)
        item['source'] = doc.xpath('string(//div[contains(text(),"出处：")]//following-sibling::div)').get('').strip()
        item['ab'] = doc.xpath('string(//div[contains(text(),"摘要：")]//following-sibling::div)').get('').strip()
        item['pd'] = doc.xpath('string(//div[contains(text(),"发布日期：")]//following-sibling::div)').get('').strip()
        item['e_ti'] = doc.xpath('string(//div[contains(text(),"英文标题：")]//following-sibling::div)').get('').strip()
        item['file'] = '0'
        item['upload_au'] = ''
        uid = item['uid']
        # org_item = await self.get_org(item['makers'])
        # item.update(org_item)
        gid = make_md5(uid)
        item['gid'] = gid
        del item['uid']
        params = self.get_params(gid, doc)
        file = Path(self.path, f'{gid}.pdf')
        return item, params,file

    async def test_download(self, uid, url):
        resp = await self.get(url)
        doc = Selector(resp.text)
        params = self.get_params(uid, doc)
        print(params)
        file = Path(self.path, f'{uid}.pdf')
        try:
            return self.download(params, file)
        except:
            return None

    async def get_info_list(self, dat_list, data, page):
        doc = Selector(dat_list)
        if page == 0:
            div_list = doc.css('div.agenciesList a')
        else:
            div_list = doc.css('a')
        gid = ''
        for i in div_list:
            uid = ''
            href = i.css('a ::attr(href)').get('').strip()
            if href:
                gid = href.split('/')[-1]
            c_ti = i.css('div.guideTitle ::text').get('').strip()
            view_num = i.css('span.guideBtmNum ::text').get('').strip().replace('人浏览', '')
            makers = i.css('div.guideLine2 ::text').get('').strip()
            item = {
                "uid": gid,
                "url": href,
                "c_ti": c_ti,
                "view_num": view_num,
                "makers": makers,
                "data_type": self.types[data['sub_type']],
                "category": self.category[data['category']],
                "dept": self.sec[data['category_sec']]}
            yield await self.get_info(uid, item)

    async def get_page(self, html, data, page=1):
        """获取页码"""
        if page == 1:
            async for row in self.get_info_list(html, data, page=0):
                yield row
        while True:
            data['page'] = page
            resp = await self.post(self.guide_list_url, data=data)
            resp = resp.json()
            try:
                has_more = resp['has_more']
                data_list = resp['data']
                async for row in self.get_info_list(data_list, data, page):
                    yield row
                if has_more.lower() == 'y':
                    page += 1
                else:
                    break
            except Exception as e:
                logger.error(f'翻页异常: [{e}]')
                break

    async def all(self):
        # if not await self.load_page(auth):
        #     await self.login(auth)  # 登录
        # await self.new_page()
        await self.get_token()  # 获取 _token
        for st, zone in self.types.items():
            for ck, category in self.category.items():
                for sk, sec in self.sec.items():
                    data = {
                        'category': ck,
                        'category_sec': sk,
                        'sub_type': st,
                        'cn_flg': '0',
                        'page': '0',
                        'page_size': '50',
                        '_token': self._token,
                    }
                    params = {
                        'category': ck,
                        'category_sec': sk,
                        'sub_type': st,
                        'year': '0',
                        'cn_flg': '0'
                    }
                    # resp = self.get_url('GET', 'https://guide.medlive.cn/publisher', params=params).text
                    resp = await self.get('https://guide.medlive.cn/guide/filter',
                                          params=params,
                                          cookies=self.cookies)
                    doc = Selector(resp.text)
                    sta = doc.css('div.noMore ::attr(style)').get('').strip()
                    async for row in self.get_page(resp.text, data):
                        yield row

                    # resp = resp.json()
                    # dat_list = resp['data']
                    # has_more = resp['has_more']
                    # async for row in self.get_info_list(dat_list, data, page=0):
                    #     yield row
                    # if has_more.lower() == 'y':
                    #     async for row in self.get_page(resp.text, data):
                    #         yield row


async def download(data: List[DownloadList], auth=None, ws=None):
    """下载 pdf 指南"""
    async with async_playwright() as playwright:
        # browser = await playwright.chromium.connect_over_cdp(ws)
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        med = MedLiveGuide(auth=auth, context=context)
        data_list = await med.browser_download(data)
        await context.close()
        await browser.close()
        return data_list


if __name__ == '__main__':
    # auth = [('123456', '000000')]  # 账号密码
    # ws = 'ws://127.0.0.1:3000'  # 如使用浏览器 登录 传入浏览器地址

    dir = Path(__file__).parent
    dlist = [
        DownloadList(url='https://guide.medlive.cn/guideline/29483', file=Path(dir, '29483.pdf')),
        DownloadList(url='https://guide.medlive.cn/guideline/29403', file=Path(dir, '29403.pdf')),
        DownloadList(url='https://guide.medlive.cn/guideline/29344', file=Path(dir, '29344.pdf')),
        DownloadList(url='https://guide.medlive.cn/guideline/29448', file=Path(dir, '29448.pdf')),
        DownloadList(url='https://guide.medlive.cn/guideline/29341', file=Path(dir, '29341.pdf')),
        DownloadList(url='https://guide.medlive.cn/guideline/29242', file=Path(dir, '29242.pdf')),
    ]
    auth = [('13530391013', '123456')]
    ws = 'ws://10.168.2.57:3000'
    import asyncio

    data_list = asyncio.run(download(dlist, auth=auth, ws=ws))
    for i in data_list:
        print(i)
