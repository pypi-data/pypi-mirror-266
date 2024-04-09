import os
import pandas as pd
from datetime import datetime

from playwright.async_api import async_playwright
import asyncio

from dmk_packages.database import database as dbs
from loguru import logger


class BigkindsCrawler:
    def __init__(self, headless=False, download_path=None, start_date=None, end_date=None):
        # playwright
        self.browser = None
        self.headless = headless
        # 다운로드 경로
        self.download_path = download_path

        # 날짜설정
        self.start_date = start_date
        self.end_date = end_date
        self.crawl_date = datetime.now()

    async def set_browser(self):
        """
        playwright 설정
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True  # 창 띄울지 말지 결정
        )
        self.context = await self.browser.new_context(accept_downloads=True)
        self.page = await self.context.new_page()
        return self

    async def playwright_crawling(self, cat):
        """
        사이트 접속 및 로그인, 검색창에 들어가 기간설정 및 카테고리 설정
        """
        try:
            # 사이트 접속
            url = "https://www.bigkinds.or.kr/v2/news/index.do"
            await self.page.goto(url, wait_until="load")
            await asyncio.sleep(2)

            # 로그인
            login_id = "scarlett@datamarketing.co.kr"
            login_pw = "dmk1234!"
            await self.page.get_by_role("button", name="로그인").click()
            await asyncio.sleep(0.5)
            await self.page.get_by_placeholder("이메일(E-mail) 주소").fill(login_id)
            await asyncio.sleep(0.3)
            await self.page.get_by_placeholder("비밀번호를 입력하세요.").fill(login_pw)
            await asyncio.sleep(0.3)
            await self.page.click("#login-btn")
            await asyncio.sleep(2)
            await self.page.wait_for_selector(
                ".ft-map > div > div > ul > li > a", state="visible"
            )
            await self.page.click(".ft-map > div > div > ul > li > a")
            await asyncio.sleep(2)
            await self.page.click(".tab-btn")
            await asyncio.sleep(0.5)

            # 기간설정하기
            date_s = await self.page.query_selector("#search-begin-date")
            date_e = await self.page.query_selector("#search-end-date")
            await date_s.fill(self.start_date)
            await asyncio.sleep(0.3)
            await date_e.fill(self.end_date)
            await asyncio.sleep(0.3)

            # 해당되는 카테고리 설정
            await self.page.click(".tab-btn.tab3")
            await asyncio.sleep(0.3)
            set_cat = await self.page.query_selector(
                f"xpath=.//span[@data-role='display' and text()='{cat}']"
            )
            await set_cat.click()
            await asyncio.sleep(0.3)
            await self.page.get_by_role("button", name="적용하기").click()
            await asyncio.sleep(2)

            # STEP 03 버튼 누르기
            await self.page.get_by_role("button", name="분석 결과 및 시각화").click()
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"playwright 크롤링오류 | error_comment : {e}")

    async def download_save_data(self, cat):
        """
        카테고리에 맞는 엑셀 저장 후 데이터변환하여 디비 적재
        """
        try:
            # 엑셀 저장
            async with self.page.expect_download() as download_info:
                await self.page.get_by_role("button", name="엑셀 다운로드").click()
            download = await download_info.value
            await download.save_as(self.download_path + download.suggested_filename)

            # 파일이름 변경
            old_filename = os.path.join(
                self.download_path,
                f"NewsResult_{self.start_date.replace('-', '')}-{self.end_date.replace('-', '')}.xlsx",
            )
            new_filename = os.path.join(
                self.download_path,
                f"NewsResult_{self.start_date.replace('-', '')}-{self.end_date.replace('-', '')}_{cat}.xlsx",
            )
            os.rename(old_filename, new_filename)

            # 엑셀파일 data_list 변환
            data_list = []
            if new_filename:
                df = pd.read_excel(new_filename)
                df = df.fillna("")
                for i in df.index:
                    data = {
                        "channel_name": "Big Kinds",
                        "category_name": cat,
                        "identifier": str(df["뉴스 식별자"][i]),
                        "regist_date": str(df["일자"][i]),
                        "press_name": df["언론사"][i],
                        "writer": df["기고자"][i],
                        "title": df["제목"][i],
                        "category_1": df["통합 분류1"][i],
                        "category_2": df["통합 분류2"][i],
                        "category_3": df["통합 분류3"][i],
                        "incident_1": df["사건/사고 분류1"][i],
                        "incident_2": df["사건/사고 분류2"][i],
                        "incident_3": df["사건/사고 분류3"][i],
                        "person": df["인물"][i],
                        "location": df["위치"][i],
                        "organization": df["기관"][i],
                        "keyword": df["키워드"][i],
                        "top50_keyword": df["특성추출(가중치순 상위 50개)"][i],
                        "contents": df["본문"][i],
                        "url": df["URL"][i],
                        "except": df["분석제외 여부"][i],
                        "created_at": self.crawl_date,
                    }
                    data_list.append(data)
            return data_list
        except Exception as e:
            logger.error(f"데이터 적재 실패 | error_comment : {e}")

    async def bigkinds_crawl(self, cat):
        """
        playwright 크롤러 전반적인 운영
        """
        # playwright 실행 및 크롤링
        logger.info(f"[{cat}] 크롤링 시작")
        await self.set_browser()
        await self.playwright_crawling(cat)
        await asyncio.sleep(1)

        # 파일 저장 및 적재
        data = await self.download_save_data(cat)
        await asyncio.sleep(0.5)

        # 브라우저 종료
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        return data
