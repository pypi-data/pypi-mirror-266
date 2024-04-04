import time
from typing import List

import pendulum
from loguru import logger
from sqlalchemy import text
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dmk_packages.database import database as db


class YoutubeDBHandler:
    # ==============================================================================
    # NOTE : 한투(postgres)로 데이터베이스 설정
    def __init__(self, target="KOREAINVESTMENT_DMK"):
        self._krinv_engine = db.get_engine(target)
        self._meta_table = "t_metadata_youtube"
        if not self._krinv_engine:
            raise ValueError("데이터베이스 엔진 설정에 실패했습니다.")
    # ==============================================================================

    # ==============================================================================
    # NOTE : json 응답에 있는 "next_page_token" 키에 해당하는 값을 metadata 테이블에 저장
    def _save_page_token(self, keyword, target_date, next_page_token):
        query = f"""
        INSERT INTO {self._meta_table} (keyword, next_page_token, target_date)
        VALUES ('{keyword}', '{next_page_token}', '{target_date}');
        """

        try:
            with self._krinv_engine.begin() as connection:
                connection.execute(text(query))
            logger.info(
                f"[{keyword}][{target_date}]: Metadata insertion completed."
            )
        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : 주어진 날짜, 키워드에 해당하는 next_page_token을 metadata 테이블에서 조회
    def _get_page_token(self, keyword, target_date):
        query = f"""
        SELECT next_page_token
        FROM {self._meta_table}
        WHERE keyword = '{keyword}'
            AND target_date = '{target_date}';
        """

        try:
            with self._krinv_engine.begin() as connection:
                result = connection.execute(text(query)).fetchone()
                return result[0] if result else False
        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : 주어진 날짜, 키워드에 해당하는 next_page_token 업데이트
    def _update_page_token(self, keyword, target_date, next_page_token):
        query = f"""
        UPDATE {self._meta_table}
        SET next_page_token = '{next_page_token}'
        WHERE keyword = '{keyword}'
            AND target_date = '{target_date}'
        """

        try:
            with self._krinv_engine.begin() as connection:
                connection.execute(text(query))
            logger.info(f"[{keyword}][{target_date}]: Metadata update completed.")
        except Exception as err:
            logger.error(err)
    # ==============================================================================


class YoutubeKeyHandler:
    # ==============================================================================
    # NOTE : 마대리(postgres)로 데이터베이스 설정
    def __init__(self, target="MADERI_AUTH"):
        self._maderi_engine = db.get_engine(target)
        self._api_key_table = 't_auth_yt_api_key_v2'
        if not self._maderi_engine:
            raise ValueError("데이터베이스 엔진 설정에 실패했습니다.")

        self.__reset_youtube_apikey()
        self._youtube_api_key = self._get_youtube_apikey()
    # ==============================================================================

    # ==============================================================================
    # NOTE : 마대리에 저장되어 있는 유튜브 API 키 리셋
    def __reset_youtube_apikey(self):
        query = f"""
        UPDATE {self._api_key_table}
        SET is_active = TRUE,
            is_valid = TRUE,
            failed_active_date = NULL,
            failed_valid_date = NULL
--         WHERE NOT is_active AND failed_active_date < CURRENT_DATE
        """
        try:
            with self._maderi_engine.begin() as connection:
                connection.execute(text(query))
            logger.info("API 키 리셋 완료")
        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : 사용 가능한 유튜브 API 키 랜덤으로 하나 가져오기
    def _get_youtube_apikey(self):
        query = f"""
        SELECT id, api_key
        FROM {self._api_key_table}
        WHERE is_valid AND is_active 
        ORDER BY RANDOM()
        LIMIT 1
        """

        try:
            with self._maderi_engine.begin() as connection:
                result = connection.execute(text(query))
            youtube_key = result.fetchone()
            if not youtube_key:
                raise ValueError("사용 가능한 유튜브 API키가 없습니다")
            return {
                "key_id": youtube_key[0],
                "api_key": youtube_key[1]
            }
        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : API 키가 할당량을 채웠을 경우 사용 불가하다 표시
    def _update_youtube_apikey_state(self, pk_id, feather):
        query = f"""
        UPDATE {self._api_key_table}
        SET is_{feather} = FALSE, 
            failed_{feather}_date = NOW()::timestamp
        WHERE id = {pk_id}
        """
        try:
            if self._maderi_engine is None:
                raise Exception("인증 정보 DB에 접근할 수 없습니다.")

            if feather not in ["valid", "active"]:
                raise Exception("사용할 수 없는 feather입니다.")

            with self._maderi_engine.begin() as connection:
                connection.execute(text(query))
        except Exception as error:
            raise Exception(error)
    # ==============================================================================

    # ==============================================================================
    # NOTE : API 키 사용 불가할 경우, 해당 키의 상태 업데이트 & 사용 가능한 키로 변경
    def _change_youtube_apikey(self, err):
        self._api_key = self._get_youtube_apikey()

        if err.resp.status == 400:
            self._update_youtube_apikey_state(self._api_key["key_id"], "valid")
        elif err.resp.status == 403:
            self._update_youtube_apikey_state(self._api_key["key_id"], "active")
    # ==============================================================================


class YoutubeCrawler(YoutubeKeyHandler, YoutubeDBHandler):
    tz = pendulum.timezone("Asia/Seoul")
    DEFAULT_DT = pendulum.yesterday(tz=tz)

    def __init__(self):
        super(YoutubeKeyHandler, self).__init__()
        super(YoutubeDBHandler, self).__init__()
        super(YoutubeCrawler, self).__init__()

        self._keywords: List[str] | None = None
        self._api_key = self._get_youtube_apikey()
        self._results = []

    def get_keywords(self) -> List[str]:
        """해당 메서드를 오버라이딩하여 키워드를 세팅합니다."""

        # NOTE: 예시를 위한 키워드입니다.
        return ["Python", "Rust", "JavaScript", "Java", "Flutter"]

    # ==============================================================================
    # NOTE : 하나의 영상에 대한 정보 반환
    def _get_video_info(self, keyword, video_info):
        try:
            youtube = build(
                serviceName="youtube",
                version="v3",
                developerKey=self._api_key["api_key"]
            )
            response = youtube.videos().list(
                id=video_info["id"]["videoId"],
                part="snippet,statistics"
            ).execute()
            time.sleep(0.1)

            video = response.get("items")[0] if len(response.get("items")) > 0 else {}
            video_id = video_info.get("id", {}).get("videoId")
            video_snippet = video.get("snippet", {})
            video_statistics = video.get("statistics", {})
            result = {
                "title": video_snippet.get("title", ""),
                "creator": video_snippet.get("channelTitle", ""),
                "contents": video_snippet.get("description", "").replace("\n\n", "").replace("\n", " "),
                "regist_date": pendulum.parse(video_snippet.get("publishedAt")),
                "view": int(video_statistics.get("viewCount", 0)),
                "recommend": int(video_statistics.get("likeCount", 0)),
                "comment": int(video_statistics.get("commentCount", 0)),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "keyword": keyword
            }
            return result

        except HttpError as err:
            key_id = self._api_key['key_id']
            self._change_youtube_apikey(err)

            logger.info(f"{err.resp.status} {err.resp.reason} 에러 발생 > {key_id}번 API 키로 변경")
            return self._get_video_info(keyword, video_info)

        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : 주어진 날짜, 키워드에 대한 전체 결과를 _results 리스트에 추가 후 반환
    def _stack_videos_info(self, keyword, target_date, page_token=None):
        try:
            next_page_token = page_token
            youtube = build(
                serviceName="youtube",
                version="v3",
                developerKey=self._api_key["api_key"]
            )
            response = youtube.search().list(
                q=keyword,
                type="video",
                part="id,snippet",
                maxResults=50,  # NOTE: 최대 50개
                pageToken=next_page_token,
                publishedAfter=target_date + "T00:00:00Z",
                publishedBefore=target_date + "T23:59:59Z",
                order="date",
                regionCode="KR",
            ).execute()
            time.sleep(0.1)

            videos = response.get("items", [])
            next_page_token = response.get("nextPageToken")
            results = [self._get_video_info(keyword, video) for video in videos]
            self._results.extend(results)
            logger.info(f"[{keyword}][{target_date}]: {len(results)} 개 추가 수집")

            if not page_token:
                self._save_page_token(keyword, target_date, next_page_token)
            else:
                self._update_page_token(keyword, target_date, next_page_token)

            if next_page_token:
                self._stack_videos_info(keyword, target_date, next_page_token)
            else:
                logger.info(f"[{keyword}][{target_date}]: {len(self._results)} 개의 영상 정보 수집 완료")

        except HttpError as err:
            key_id = self._api_key['key_id']
            self._change_youtube_apikey(err)

            logger.info(f"{err.resp.status} {err.resp.reason} 에러 발생 > {key_id}번 API 키로 변경")
            return self._stack_videos_info(keyword, target_date, next_page_token)

        except Exception as err:
            logger.error(err)
    # ==============================================================================

    # ==============================================================================
    # NOTE : _results 값 반환
    def get_videos_info(self, keywords_target_dates):
        keyword, target_date = keywords_target_dates
        next_page_token = self._get_page_token(keyword, target_date)

        if next_page_token == 'None':
            logger.info(f"[{keyword}][{target_date}]: 이미 수집 완료")
        elif not next_page_token:
            # logger.info(f"[{keyword}][{target_date}]: 수집 필요")
            self._stack_videos_info(keyword, target_date)
        else:
            logger.info(f"[{keyword}][{target_date}]: next_page_token 업데이트 필요")
            self._update_page_token(keyword, target_date, next_page_token)

        results = self._results.copy()
        self._results = []
        return results
    # ==============================================================================
