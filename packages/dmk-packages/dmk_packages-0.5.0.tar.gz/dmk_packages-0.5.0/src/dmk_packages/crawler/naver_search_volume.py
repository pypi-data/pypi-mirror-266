import base64
import hashlib
import hmac
import json
from typing import List, TypedDict

import pendulum
import requests
from loguru import logger
from sqlalchemy import text

from dmk_packages.database import database as db

tz = pendulum.timezone("Asia/Seoul")

# fmt: off
DatalabData = TypedDict("Data", {"period": str, "ratio": float})
DatalabResult = TypedDict("DatalabData", {"keyword": str, "data": DatalabData})
SearchadResult = TypedDict("SearchadResult", {"keyword": str, "monthlyPcQcCnt": int, "monthlyMobileQcCnt": int})
# fmt: on


class NaverSearchVolumeKeyHandler:
    def __init__(self, target="MADERI_AUTH"):
        self._engine = db.get_engine(target)
        if not self._engine:
            raise ValueError("데이터베이스 엔진 설정에 실패했습니다.")

        self.__reset_datalab_key()
        self._datalab_key = self._get_datalab_key()
        self._searchad_key = self._get_searchad_key()

    def __reset_datalab_key(self):
        try:
            query = """
            UPDATE t_auth_naver_datalab_key_v2
            SET is_active          = TRUE,
                failed_active_date = NULL
            WHERE NOT is_active
              AND failed_active_date < CURRENT_DATE;
            """

            with self._engine.begin() as connection:
                connection.execute(text(query))
        except Exception as err:
            logger.error(err)

    def _get_searchad_key(self):
        try:
            query = """
            SELECT id, customer_id, access_license, private_key
            FROM t_auth_naver_searchad_key_v2
            WHERE is_valid
            ORDER BY RANDOM()
            LIMIT 1;
            """

            with self._engine.begin() as connection:
                result = connection.execute(text(query))

            searchad_key = result.fetchone()

            if not searchad_key:
                raise ValueError("사용 가능한 검색광고 키가 없습니다.")

            return {
                "key_id": searchad_key[0],
                "customer_id": searchad_key[1],
                "access_license": searchad_key[2],
                "private_key": searchad_key[3],
            }
        except Exception as err:
            logger.error(err)

    def _get_datalab_key(self):
        try:
            query = """
            SELECT id, client_id, client_secret
            FROM t_auth_naver_datalab_key_v2
            WHERE is_auth AND is_active
            ORDER BY RANDOM()
            LIMIT 1;
            """

            with self._engine.begin() as connection:
                result = connection.execute(text(query))

            datalab_key = result.fetchone()

            if not datalab_key:
                raise ValueError("사용 가능한 데이터랩 키가 없습니다.")

            return {
                "key_id": datalab_key[0],
                "client_id": datalab_key[1],
                "client_secret": datalab_key[2],
            }
        except Exception as err:
            logger.error(err)

    # NOTE: 검색광고 API에 대해서는 제한량이 없다고 하여 사용이 안될 수 있다.
    #     : 하지만 만약 그외의 이유로 키를 사용하지 못하게 될 경우를 대비해야한다.
    def _update_searchad_key(self, pk_id, feather):
        try:
            if self._engine is None:
                raise Exception("인증 정보 DB에 접근할 수 없습니다.")

            if feather not in ["valid"]:
                raise Exception("사용할 수 없는 feather입니다.")

            query = f"""
                    UPDATE t_auth_naver_searchad_key_v2
                    SET is_{feather} = FALSE, failed_{feather}_at = CURRENT_DATE
                    WHERE id = {pk_id};
                    """

            with self._engine.begin() as connection:
                connection.execute(text(query))

        except Exception as error:
            raise Exception(error)

    def _update_datalab_key(self, pk_id, feather):
        try:
            if self._engine is None:
                raise Exception("인증 정보 DB에 접근할 수 없습니다.")

            if feather not in ["auth", "active"]:
                raise Exception("사용할 수 없는 feather입니다.")

            query = f"""
                    UPDATE t_auth_naver_datalab_key_v2
                    SET is_{feather} = FALSE, failed_{feather}_date = CURRENT_DATE
                    WHERE id = {pk_id};
                    """

            with self._engine.begin() as connection:
                connection.execute(text(query))

        except Exception as error:
            raise Exception(error)


class NaverSearchVolumeCrawler(NaverSearchVolumeKeyHandler):
    DEFAULT_DT = pendulum.yesterday(tz=tz)
    DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"
    SEARCHAD_URL = "https://api.naver.com/keywordstool"

    LESS_THAN_10 = "< 10"
    MPQC = "monthlyPcQcCnt"
    MMQC = "monthlyMobileQcCnt"

    def __init__(self, date_from=None, date_until=None):
        super(NaverSearchVolumeCrawler, self).__init__()

        self._date_range = []
        self._date_from = pendulum.parse(date_from) if date_from else self.DEFAULT_DT
        self._date_until = pendulum.parse(date_until) if date_until else self.DEFAULT_DT

        self._keywords: List[str] | None = None
        self._keywords_bundle: List[List[str]] | None = None

    def _set_date_range(self, target_date):
        try:
            # NOTE: 30일전 날짜를 구해야한다.
            #     : 타겟날짜도 포함하기에 코드에서는 29일을 차감한다.
            date_thirty_days_ago = target_date.subtract(days=29)

            self._date_range.append([date_thirty_days_ago, target_date])

            if self._date_from < date_thirty_days_ago:
                return self._set_date_range(date_thirty_days_ago.subtract(days=1))
        except Exception as error:
            logger.error(error)

    def _set_keywords(self, keywords: List[str]):
        self._keywords = keywords

    def _set_keywords_bundle(self, keywords: List[str]):
        try:
            keywods_bundle = [keywords[i : i + 5] for i in range(0, len(keywords), 5)]
            self._keywords_bundle = keywods_bundle
        except Exception as error:
            logger.error(error)

    def get_keywords(self) -> List[str]:
        """해당 메서드를 오버라이딩하여 키워드를 세팅합니다."""

        # NOTE: 예시를 위한 키워드입니다.
        return ["Python", "Rust", "JavaScript", "Java", "Flutter"]

    def get_searchad_data(self, keywords_bundle: List[str]) -> List[SearchadResult]:
        """
        네이버 검색광고 API 데이터 가져오기

        API 문서: https://naver.github.io/searchad-apidoc/#/tags/RelKwdStat
        """
        try:
            if len(keywords_bundle) > 5:
                raise ValueError("keywords_bundle 리스트는 최대 5개까지만 허용됩니다.")

            hint_keywords = ",".join(
                [k.replace(" ", "").upper() for k in keywords_bundle]
            )
            hint_keywords_map = {k.replace(" ", "").upper(): k for k in keywords_bundle}

            timestamp = str(round(pendulum.now().timestamp() * 1000))
            signature = base64.b64encode(
                hmac.new(
                    bytes(self._searchad_key["private_key"], "UTF-8"),
                    bytes(f"{timestamp}.GET./keywordstool", "UTF-8"),
                    digestmod=hashlib.sha256,
                ).digest()
            )

            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Timestamp": timestamp,
                "X-API-KEY": self._searchad_key["access_license"],
                "X-Customer": self._searchad_key["customer_id"],
                "X-Signature": signature,
            }

            response = requests.get(
                url=self.SEARCHAD_URL,
                headers=headers,
                params={"hintKeywords": hint_keywords},
            )

            if not response.ok:
                raise Exception(response.json().get("title"))

            target_keyword_hits = 0
            searchad_data = []
            result = response.json()

            for kwd in result.get("keywordList"):
                if kwd["relKeyword"] in hint_keywords_map:

                    kwd[self.MPQC] = (
                        kwd[self.MPQC] if kwd[self.MPQC] != self.LESS_THAN_10 else 9
                    )
                    kwd[self.MMQC] = (
                        kwd[self.MMQC] if kwd[self.MMQC] != self.LESS_THAN_10 else 9
                    )

                    searchad_data.append(
                        {
                            "keyword": hint_keywords_map[kwd["relKeyword"]],
                            "monthlyPcQcCnt": kwd[self.MPQC],
                            "monthlyMobileQcCnt": kwd[self.MMQC],
                        }
                    )

                    target_keyword_hits += 1
                    if target_keyword_hits == len(keywords_bundle):
                        break
            return searchad_data
        except Exception as error:
            raise Exception(error)

    def get_datalab_data(
        self, keywords_bundle: List[str], start_dt, end_dt
    ) -> List[DatalabResult]:
        """
        네이버 데이터랩 API 데이터 가져오기

        API 문서: https://developers.naver.com/docs/serviceapi/datalab/search/search.md#python
        """
        try:
            if len(keywords_bundle) > 5:
                raise ValueError("keywords_bundle 리스트는 최대 5개까지만 허용됩니다.")

            datalab_data = []

            headers = {
                "X-Naver-Client-Id": self._datalab_key.get("client_id"),
                "X-Naver-Client-Secret": self._datalab_key.get("client_secret"),
                "Content-Type": "application/json",
            }
            body = {
                "startDate": start_dt,
                "endDate": end_dt,
                "timeUnit": "date",
                "keywordGroups": [
                    {"groupName": k, "keywords": [k]} for k in keywords_bundle
                ],
            }
            response = requests.post(
                url=self.DATALAB_URL, headers=headers, data=json.dumps(body)
            )

            if not response.ok:
                self._datalab_key = self._get_datalab_key()

                if response.status_code == 401:
                    # ============================================================
                    # NOTE: 데이터랩 인증 실패
                    self._update_datalab_key(self._datalab_key["key_id"], "auth")
                    # ============================================================
                elif response.status_code == 429:
                    # ============================================================
                    #  NOTE: 데이터랩 호출 한도 초과시 업데이트
                    self._update_datalab_key(self._datalab_key["key_id"], "active")
                    # ============================================================

                return self.get_datalab_data(keywords_bundle, start_dt, end_dt)

            results = response.json().get("results")

            for result in results:
                keyword = result.get("title", "")
                data = result.get("data", [])

                temp_data = data.copy()
                existing_dates = {d["period"] for d in data}

                start_date = pendulum.from_format(start_dt, "YYYY-MM-DD")
                end_date = pendulum.from_format(end_dt, "YYYY-MM-DD")

                current_date = start_date
                while current_date <= end_date:
                    current_date_str = current_date.strftime("%Y-%m-%d")
                    if current_date_str not in existing_dates:
                        temp_data.append({"period": current_date_str, "ratio": 0.0})
                    current_date = current_date.add(days=1)

                temp_data.sort(key=lambda x: x["period"])
                datalab_data.append({"keyword": keyword, "data": temp_data})
            return datalab_data
        except Exception as error:
            raise Exception(error)

    def calc_search_volume(
        self,
        keywords_bundle,
        searchad_data: List[SearchadResult],
        datalab_data: List[DatalabResult],
    ):
        try:
            search_volume = []

            for kwd in keywords_bundle:
                tgt_searchad_datum = [d for d in searchad_data if d["keyword"] == kwd]
                tgt_datalab_datum = [d for d in datalab_data if d["keyword"] == kwd]

                if tgt_searchad_datum and tgt_datalab_datum:
                    monthly_pc_volume = tgt_searchad_datum[0].get(self.MPQC)
                    monthly_mo_volume = tgt_searchad_datum[0].get(self.MMQC)

                    total_volume = monthly_pc_volume + monthly_mo_volume
                    total_ratio = sum(
                        [d["ratio"] for d in tgt_datalab_datum[0].get("data")]
                    )

                    volume_per_ratio = (
                        total_volume / total_ratio if total_ratio > 0 else 0
                    )

                    for d in tgt_datalab_datum[0].get("data"):
                        new_data = {
                            "keyword_text": kwd,
                            "keyword_date": pendulum.parse(d["period"], tz=tz),
                            "keyword_volume": int(d["ratio"] * volume_per_ratio),
                            "collected_at": pendulum.today(),
                        }
                        search_volume.append(new_data)
            return search_volume
        except Exception as error:
            logger.error(error)

    def get_search_volume(self):
        try:
            results = []

            if not self._searchad_key or not self._datalab_key:
                return results

            self._set_date_range(target_date=self._date_until)

            self._set_keywords(self.get_keywords())
            self._set_keywords_bundle(keywords=self._keywords)

            for kwds_bundle in self._keywords_bundle:
                searchad_data = self.get_searchad_data(kwds_bundle)

                for date_range in self._date_range:
                    start_dt, end_dt = [d.strftime("%Y-%m-%d") for d in date_range]
                    logger.info(f"{start_dt} ~ {end_dt} {kwds_bundle}")
                    datalab_data = self.get_datalab_data(
                        kwds_bundle,
                        start_dt,
                        end_dt,
                    )

                    search_volume = self.calc_search_volume(
                        kwds_bundle,
                        searchad_data,
                        datalab_data,
                    )
                    results.extend(search_volume)
            return results
        except Exception as error:
            logger.error(error)


if __name__ == "__main__":
    try:
        naver_search_volume_crawler = NaverSearchVolumeCrawler()
        search_volume = naver_search_volume_crawler.get_search_volume()

        for vol in search_volume:
            logger.debug(vol)
    except Exception as error:
        logger.error(error)
