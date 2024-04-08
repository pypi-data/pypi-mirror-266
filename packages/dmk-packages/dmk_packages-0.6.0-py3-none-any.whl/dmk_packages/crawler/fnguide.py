import os
from datetime import date, datetime, timedelta

import asyncio
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from dmk_packages.database import database as dbs
from . import fnguide_pdf_update as update
from loguru import logger


class FnguideCrawler:
    def __init__(self, download_path=None, backup_path=None):
        # playwright
        self.browser = None
        self.page = None
        # 다운로드 경로
        self.download_path = download_path
        self.backup_path = backup_path

        # 날짜설정
        yesterday = date.today() - timedelta(1)
        self.start_date = yesterday.strftime("%Y-%m-%d")
        self.end_date = yesterday.strftime("%Y-%m-%d")
        self.crawl_date = datetime.now()

        # 카테고리
        self.cat_list = [
            "기업",
            "산업",
            "경제",
            "주식",
            "채권",
            "파생",
            "외환",
            "중국",
            "펀드",
        ]
        # 다운로드 에러가 가는 url 리스트
        self.url_e = []

        # 데이터베이스
        self.get_engine = dbs.get_engine(target="KOREAINVESTMENT_DMK")
        self.TARGET_TABLE = "t_fnguide_file_info"

    async def set_browser(self):
        """
        playwright 설정
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True  # 창띄울지 말지 결정
        )
        self.context = await self.browser.new_context(accept_downloads=True)
        self.page = await self.context.new_page()
        return self

    async def login_set_date(self):
        """
        사이트 접속 및 로그인, 검색창에 들어가 기간설정
        """
        # 로그인
        user_id = "hantoo"
        password = "kimdmk1!"
        url_fnguide = "https://www.fnguide.com/"
        await self.page.goto(url_fnguide, wait_until="load")
        await asyncio.sleep(2)
        await self.page.fill('input[name="MemberID"]', user_id)
        await asyncio.sleep(0.3)
        await self.page.fill('input[name="PassWord"]', password)
        await self.page.click(".btn--login")
        await asyncio.sleep(2)

        # fnresearch 들어가서 기간설정 후 검색
        await self.page.click(".gnb--1dep > .p1")
        await asyncio.sleep(2)
        await self.page.wait_for_selector("#frDate", state="visible")
        await self.page.wait_for_timeout(1000)
        await self.page.fill("#frDate", self.start_date)
        await asyncio.sleep(0.3)
        await self.page.fill("#toDate", self.end_date)
        await asyncio.sleep(0.3)
        await self.page.locator("#srchBtn").click()
        await asyncio.sleep(1)

    async def fetch_data(self, cat):
        """
        카테고리에 맞는 데이터 크롤링 후 데이터리스트 변환
        """
        data_list = []
        while True:
            table = await self.page.query_selector("#resultDivGrid")
            if await table.query_selector(".nodata"):  # 검색결과가 없는 경우
                break
            rows = await table.query_selector_all("tbody > tr")
            for row in rows:
                tds = await row.query_selector_all("td")
                regist_date = await tds[0].inner_text()
                category_name = cat
                title = await tds[1].inner_text()
                provider = await tds[4].inner_text()
                writer = await tds[3].inner_text()
                url_tag = await tds[1].eval_on_selector(
                    "a", 'element => element.getAttribute("href")'
                )
                url = f"https://www.fnguide.com{url_tag}"
                url_idx = url.split("bulletkind=")[-1]
                filename = url_idx + "_" + regist_date + ".pdf"

                # pdf 다운로드
                try:
                    # 이미 다운로드 되어있는 파일 목록
                    os.chdir(self.download_path)
                    file_names = os.listdir()
                    # 오류나는 파일과 이미 다운로드가 되어있다면 패스 아니라면 다운로드 진행
                    if (url_tag not in self.url_e) and (filename not in file_names):
                        async with self.page.expect_download(
                            timeout=15000
                        ) as download_info:
                            pdf = await row.query_selector(".btn--get")
                            await pdf.click()
                        download = await download_info.value
                        await download.save_as(
                            self.download_path + url_idx + "_" + regist_date + ".pdf"
                        )
                        await asyncio.sleep(0.5)
                except PlaywrightTimeoutError:
                    logger.error(
                        f"[{cat}][{regist_date}][{title}]의 pdf 파일 다운로드 중 오류"
                    )
                    await self.context.close()
                    await self.browser.close()
                    # 오류난 파일의 url_tag 추가
                    self.url_e.append(url_tag)
                    # 다시 실행
                    await self.fnguide_crawl(cat)

                # 찾은 데이터 list에 append
                data = {
                    "channel_name": "Fnguide",
                    "category_name": category_name,
                    "regist_date": regist_date,
                    "title": title,
                    "writer": writer,
                    "provider": provider,
                    "url": url,
                    "created_at": self.crawl_date,
                }
                data_list.append(data)

            # 반목문 중단 or 다음 페이지
            try:
                await self.page.click(".paging > .btn--next", timeout=1000)
                await asyncio.sleep(0.5)
            except PlaywrightTimeoutError:
                break
        await asyncio.sleep(1)
        await self.context.close()
        await self.browser.close()
        return data_list

    async def fnguide_crawl(self, cat):
        """
        playwright 크롤러 전반적인 운영
        """
        try:
            # playwright 실행 및 크롤링
            logger.info(f"[{cat}] 크롤링 시작")
            await self.set_browser()
            await self.login_set_date()
            # 해당 카테고리 클릭 및 검색
            await self.page.click(
                f'//*[@id="resultDivTabs"]/ul/li/button[contains(text(), "{cat}")]'
            )
            await asyncio.sleep(0.5)
            data = await self.fetch_data(cat)

            # =========================================
            # NOTE: 데이터베이스 저장
            if len(data) > 0:
                dbs.insert_to_postgres(
                    engine=self.get_engine,
                    name=self.TARGET_TABLE,
                    values=data,
                )
                logger.info("적재 완료")
            else:
                logger.info("데이터가 없어 적재 안함")
            # =========================================
        except Exception as e:
            logger.error(e)

    async def run_crawler(self):
        """
        크롤러 작동 시작
        """
        try:
            logger.info("## FnGuide 크롤링 시작 ##")
            cat_list = self.cat_list  # 카테고리 리스트
            for cat in cat_list:
                await self.fnguide_crawl(cat)
            await self.playwright.stop()

            logger.info("## 크롤링 데이터 적재 완료. PDF 변환 및 적재 시작 ##")
            pdf = update.UpdateFnGuidePdfData(
                download_path=self.download_path, backup_path=self.backup_path
            )
            pdf.update_pdf_data()
        except Exception as e:
            logger.error(f"run_crawler 오류 : {e}")


if __name__ == "__main__":
    crawler = FnguideCrawler()
    asyncio.run(crawler.run_crawler())
