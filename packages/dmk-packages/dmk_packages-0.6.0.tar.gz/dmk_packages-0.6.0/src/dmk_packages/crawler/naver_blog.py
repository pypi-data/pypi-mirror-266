import json
from typing import TypedDict
from urllib.parse import urlencode

import requests
from fake_useragent import UserAgent
from loguru import logger

BlogItem = TypedDict(
    "BlogItem",
    {
        "domainIdOrBlogId": str,
        "logNo": int,
        "gdid": str,
        "postUrl": str,
        "title": str,
        "noTagTitle": str,
        "contents": str,
        "nickName": str,
        "blogName": str,
        "profileImgUrl": str,
        "addDate": int,
        "thumbnails": list[str],
        "product": None,  # FIXME: 다른 데이터는 어떤 것인지 파악되지 않음
        "marketPost": bool,
        "hasThumbnail": bool,
    },
)


class NaverBlogCrawler:
    BASE_URL = "https://section.blog.naver.com/ajax/SearchList.naver"
    REFERER_URL = "https://section.blog.naver.com/Search/Post.naver"

    def __init__(self):
        self._user_agent = UserAgent(min_percentage=1.1, os=["windows", "macos"])

    def get_blog_items(self, keyword: str, page: int, start_dt: str, end_dt: str):
        base_url_params = {
            "keyword": keyword,
            "currentPage": page,
            "startDate": start_dt,
            "endDate": end_dt,
            "orderBy": "recentdate",
            "countPerPage": "15",
            "type": "post",
        }

        referer_url_params = {
            "keyword": keyword,
            "startDate": start_dt,
            "endDate": end_dt,
            "orderBy": "recentdate",
            "rangeType": "PERIOD",
            "pageNo": "1",
        }

        headers = {
            "User-agent": self._user_agent.random,
            "Referer": f"{self.REFERER_URL}?{urlencode(referer_url_params)}",
        }

        response = requests.get(
            f"{self.BASE_URL}?{urlencode(base_url_params)}", headers=headers
        )

        data = json.loads(response.text.split(",", 1)[-1].strip())

        total_count = data.get("result", {}).get("totalCount", [])
        search_list = data.get("result", {}).get("searchList", [])

        logger.debug(search_list[0])

        return {"total_count": total_count, "search_list": search_list}

    def parse_blog_item(self): ...


if __name__ == "__main__":
    naver_blog_crawler = NaverBlogCrawler()

    naver_blog_crawler.get_blog_items("파이썬", 1, "2024-03-19", "2024-03-19")
