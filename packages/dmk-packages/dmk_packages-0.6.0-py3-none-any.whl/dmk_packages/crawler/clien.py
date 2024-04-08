import re
import time
import pendulum
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
import random
from dmk_packages.database import database as dbs
from sqlalchemy import MetaData, Table, select, union, func
from datetime import date, timedelta


class ClienCmStock:
    def __init__(self):
        # 크롤러
        self._user_agent = UserAgent(min_percentage=1.1, os=["windows", "macos"])
        self._session = requests.session()
        self._max_board_sn = 0
        self._min_board_sn = 0
        self.BASE_URL = "https://www.clien.net"

        # 날짜설정
        yesterday = date.today() - timedelta(1)
        self.start_date = yesterday.strftime("%Y-%m-%d 00:00:00")
        self.end_date = yesterday.strftime("%Y-%m-%d 00:00:00")

        # 데이터베이스
        self.get_engine = dbs.get_engine(target="KOREAINVESTMENT_DMK")
        self.DATA_TABLE = "t_clien_post"

    def _get_keyword_list(self):
        """
        검색할 keyword_list를 가져오는 코드
        """
        table_name1 = "t_han_keyword_list"
        table_name2 = "t_han_code_list"

        metadata = MetaData()
        metadata.bind = self.get_engine
        table1 = Table(table_name1, metadata, autoload_with=self.get_engine)
        table2 = Table(table_name2, metadata, autoload_with=self.get_engine)

        stmt1 = select(table1.c.keyword)
        stmt2 = select(table2.c.kor_name).where(table2.c.kor_name.like("ACE%%"))
        u = union(stmt1, stmt2)

        with self.get_engine.begin() as connection:
            result = connection.execute(u)
            keywords = [row[0] for row in result.fetchall()]
        return keywords

    def _check_data_table(self, keyword, category, table):
        """
        keyword 및 category에 해당하는 board_sn컬럼의 max, min 값을 가져오는 컬럼
        """
        metadata = MetaData()
        metadata.bind = self.get_engine
        table = Table(table, metadata, autoload_with=self.get_engine)

        stmt = select(func.max(table.c.board_sn), func.min(table.c.board_sn)).where(
            (table.c.category_name == category) & (table.c.keyword == keyword)
        )

        with self.get_engine.begin() as connection:
            result = connection.execute(stmt)
            a = result.fetchall()
            max_board_sn = a[0][0] or 0
            min_board_sn = a[0][1] or 0

        return max_board_sn, min_board_sn

    def _run_list_crawl(self, keyword: str, category: str, page: int):
        """
        해당되는 데이터 가져오기
        """
        try:
            headers = {"User-agent": self._user_agent.random}
            target_url = self.BASE_URL + "/service/search"
            params = {
                "q": keyword,
                "p": page,
                "sort": "recency",
                "boardCd": category,
                "isBoard": True,
            }

            response = self._session.get(
                target_url, headers=headers, params=params, timeout=3
            )
            time.sleep(random.uniform(1, 10))

            soup = BeautifulSoup(response.text, "html.parser")

            keyword_posts = self._retrieve_posts(soup, keyword, category)
            next_page = self._retrieve_next_page(soup)
            return keyword_posts, next_page
        except Exception as error:
            logger.error(error)

    def _retrieve_posts(self, soup: BeautifulSoup, keyword: str, category: str):
        """
        데이터 수집
        """
        try:
            items = soup.select(".list_item.symph_row.jirum")
            results = []
            start_date = pendulum.parse(self.start_date)
            end_date = pendulum.parse(self.end_date)

            for item in items:
                board_sn = int(item["data-board-sn"])
                regist_date = pendulum.parse(item.select_one(".timestamp").text)

                if self._min_board_sn <= board_sn <= self._max_board_sn:
                    continue

                if start_date < regist_date < end_date:
                    comment = int(item["data-comment-count"])
                    url = self.BASE_URL + item.select_one(".subject_fixed")["href"]

                    data = {
                        "category_name": category,
                        "regist_date": regist_date,
                        "comment": comment,
                        "url": url,
                        "keyword": keyword,
                        "board_sn": board_sn,
                    }
                    results.append(data)
            return results
        except Exception as error:
            logger.error(error)

    def _retrieve_next_page(self, soup: BeautifulSoup):
        """
        다음 페이지 가져오기 없으면 패스
        """
        pages = soup.select(".board-nav-page")
        if len(pages) <= 1:
            return None
        next_btn_exists = bool(soup.select_one(".board-nav-next"))

        last_item = soup.select(".list_item")[-1]
        last_item_timestamp = last_item.select_one(".timestamp").text

        if pendulum.parse(self.start_date) > pendulum.parse(last_item_timestamp):
            return None

        for idx, page in enumerate(pages):
            if "active" in page.get("class", []):
                if next_btn_exists or idx + 1 < len(pages):
                    return idx + 1
                break

        return None

    def _run_item_crawl(self, posts):
        """
        해당 게시물의 내용 가져오는 전반적인 내용
        """
        try:
            results = []
            for post in posts:
                logger.info(f"[적재하는 url: {post['url']}")

                details = self._retrieve_post_detail(post.get("url"))
                results.append({**post, **details})

            return results
        except Exception as error:
            logger.error(error)

    def _retrieve_post_detail(self, post_url):
        """
        해당 게시물의 내용 정제해서 가져오기
        """
        headers = {"User-agent": self._user_agent.random}
        response = self._session.get(post_url, headers=headers)
        time.sleep(random.uniform(1, 10))

        soup = BeautifulSoup(response.text, "html.parser")

        title_elems = soup.select(".post_subject span")
        title = next(
            (
                elem.text.strip()
                for elem in title_elems
                if "post_category" not in elem.get("class", [])
            ),
            None,
        )

        view = soup.select_one(".view_count strong").text.strip().replace(",", "")

        contents = soup.select_one(".post_article").text.strip()
        # 연속된 두 개 이상의 개행을 한 개의 개행으로 줄임
        contents = re.sub(r"\n\n", "\n", contents)
        # 개행 문자를 공백으로 치환
        contents = re.sub(r"\n", " ", contents)
        # \xa0, \xad, \ufeff 문자 제거
        contents = re.sub(r"[\xa0\xad\ufeff]+", "", contents)
        # 두 개 이상의 공백을 단일 공백으로 치환
        contents = re.sub(r" {2,}", " ", contents)

        return {"view": int(view), "title": title, "contents": contents}

    def _process_target(self, target, page=0):
        """
        크롤러 전반적인 운영
        """
        keyword, category = target
        logger.info(f"[{category}][{keyword}] 크롤링 시작")
        self._max_board_sn, self._min_board_sn = self._check_data_table(
            keyword=keyword, category=category, table=self.DATA_TABLE
        )

        keyword_posts, next_page = self._run_list_crawl(keyword, category, page)
        keyword_results = self._run_item_crawl(keyword_posts)

        # =========================================
        # NOTE: 데이터베이스 저장
        try:
            if len(keyword_results) > 0:
                dbs.insert_to_postgres(
                    engine=self.get_engine,
                    name=self.DATA_TABLE,
                    values=keyword_results,
                    index_elements=[
                        "category_name",
                        "keyword",
                        "regist_date",
                        "board_sn",
                    ],
                )
                logger.info("데이터 적재 완료")
            else:
                logger.info("적재할 데이터 없음")
        except Exception as e:
            logger.error(f"데이터 적재 실패 | error_comment : {e}")
        # =========================================
        if next_page:
            self._process_target(target, next_page)
            logger.info("다음 페이지 적재 시작")

    def run_crawler(self):
        """
        크롤러 작동 시작
        """
        try:
            logger.info("## Clien 크롤링 시작 ##")
            # 타켓 키워드 만들기
            keywords = self._get_keyword_list()
            targets = [
                (keyword, category)
                for category in [
                    "cm_stock",
                    "park",
                    "kin",
                ]  # 주식한당, 모두의공원, 아무거나질문
                for keyword in sorted(keywords)
            ]
            for target in targets:
                self._process_target(target)
            logger.info("## 크롤링 데이터 적재 완료 ##")
        except Exception as error:
            logger.error(error)


clawer = ClienCmStock()
clawer.run_crawler()
