# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/12/22 16:02
# 医脉通登录
import json
import time
from pathlib import Path
from random import choice
from typing import List, Dict
import logging

import requests
from parsel import Selector
from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import async_playwright
from playwright.async_api._generated import Page, BrowserContext

from duspider.tools import get_ua

logger = logging.getLogger("duspider.medlivelogin")

from typing import List

from pydantic import BaseModel


class DownloadList(BaseModel):
    url: str
    file: Path
    sta: bool = False
    msg: str = ''


class CookieItem(BaseModel):
    browserCookies: List[SetCookieParam]

    def get_cookie(self) -> Dict:
        cookies_dict = {}
        for row in self.browserCookies:
            if 'medlive' in row["domain"]:
                cookies_dict[row["name"]] = row["value"]
        return cookies_dict


# with open(r'D:\WorkD\DUSPIDER\duspider\cookies.json', encoding='utf-8') as f:
#     data = f.read()
#     if data:
#         co = CookieItem(**json.loads(data))
#         print(type(co.browserCookies[0]))
class MedLiveLogin:
    def __init__(self, context: BrowserContext, auth: List, path):
        self.login_url = 'https://www.medlive.cn/auth/login'
        self.download_url = 'https://guide.medlive.cn/guide/download'
        # self.params = {'service': 'https://www.medlive.cn/'}
        self.params = {'service': 'https://guide.medlive.cn/'}
        self.context = context
        self.page = None

        self.headers = {
            'DNT': '1',
            'Origin': 'https://www.medlive.cn',
            'Pragma': 'no-cache',
            # 'Referer': url,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': get_ua(),
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'}
        self.user_list: List[(str, str)] = auth
        self.cookies_path = Path(path.parent, 'cookies.json')
        if not self.cookies_path.exists():
            self.cookies_path.touch()

    async def login(self, auth):
        """耕录账号"""
        await self.new_page()
        await self.page.goto(self.login_url)
        await self.page.click('div.rightTab-R')
        user, pwd = auth
        await self.page.fill('#username', user)
        await self.page.fill('#showPassword', pwd)
        time.sleep(1)
        await self.page.click('#loginsubmit')
        time.sleep(1)
        await self.page.reload()
        time.sleep(1)
        cookies = await self.context.cookies()
        browser_cookies = {user: {"browserCookies": cookies}}
        await self.save_cookies(browser_cookies)

    async def save_cookies(self, cookie):
        """保存数据"""
        if cookie:
            with open(self.cookies_path, encoding='utf-8') as f:
                data = f.read()
                if data.strip():
                    cookies = json.loads(data)
                    cookies.update(cookie)
                else:
                    cookies = cookie

            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False)

    async def new_page(self):
        """创建浏览器页面"""
        self.page = await self.context.new_page()
        await self.add_js()

    async def add_js(self):
        """添加防止识别 js"""
        js = """Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"""
        await self.page.add_init_script(js)

    async def load_page(self, auth) -> bool:
        """加载cookies 到浏览器中"""
        if self.page:
            return True
        cookies = self.get_cookies(auth)
        logger.info(f'cookies2: {cookies}')
        if cookies:
            await self.context.add_cookies(cookies.browserCookies)
            await self.new_page()
            await self.page.goto('https://guide.medlive.cn/')
            time.sleep(0.1)
            sta = await self.page.query_selector('#login')
            if sta:
                return False
            return True
        else:
            return False

    def get_cookies(self, auth) -> CookieItem:
        with open(self.cookies_path, encoding='utf-8') as f:
            data = f.read()
            if data.strip():
                cookies = json.loads(data)
                cookie = cookies.get(auth[0])
                if cookie:
                    return CookieItem(**cookie)

    def get_user(self):
        """随机获取用户数据"""
        return choice(self.user_list)

    async def browser_download(self, auth, dw: DownloadList) -> DownloadList:
        """浏览器下载"""
        if not await self.load_page(auth):
            await self.login(auth)

        page1 = await self.context.new_page()
        await page1.goto(dw.url)
        # await self.page.goto(dw.url)
        page3 = None
        try:
            # await self.page.goto("https://guide.medlive.cn/guideline/29341")
            async with page1.expect_download() as download2_info:
                async with page1.expect_popup() as page3_info:
                    await page1.locator(".sideBtn").first.click()
                page3 = await page3_info.value
            download = await download2_info.value
            await download.save_as(dw.file)
            dw.sta = True
        except:
            dw.sta = False
        if page3:
            time.sleep(1)
            try:
                html = await page3.content()
            except:
                html = ''
            else:
                await page3.close()
            if '超过本日最大下载次数限制' in html:
                dw.msg = '超过本日最大下载次数限制'
                await self.page.close()  # 关闭浏览器
                self.page = None
                await self.context.clear_cookies()  # 清除 cookies

        await page1.close()

        return dw


if __name__ == '__main__':
    import asyncio

    auth = [('123456', '000000')]  # 账号密码


    # ws = 'ws://127.0.0.1:3000'  # 如使用浏览器 登录 传入浏览器地址
    # med = MedLiveLogin(auth=auth, ws=ws)
    # asyncio.run(med.test(url=url))

    async def t1():
        async with async_playwright() as playwright:
            # browser = await playwright.chromium.connect_over_cdp(ws)
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            med = MedLiveLogin(context=context, auth=auth)
            aa = await med.load_page()
            print('aa:', aa)


    asyncio.run(t1())
