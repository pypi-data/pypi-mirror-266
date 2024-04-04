import pandas as pd
from loguru import logger
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from src.dmk_packages.database import database as db
from src.dmk_packages.crawler.youtube import YoutubeCrawler


class YoutubeCrawlerTest(YoutubeCrawler):
    def __init__(self, config, date_from=None, date_until=None):
        super().__init__()
        self.config = config
        self._engine = db.get_engine("KOREAINVESTMENT_DMK")
        self._keyword_table = "t_han_keyword_list"
        self._target_table = "t_youtube_daily_post"
        self._date_from = date_from
        self._date_until = date_until

    def get_keywords(self):
        query = f"""
        SELECT keyword
        FROM {self._keyword_table}
        """
        try:
            keywords_df = pd.read_sql_query(query, con=self._engine)
            return sorted(keywords_df.keyword.tolist())
        except Exception as error:
            raise Exception(error)

    def insert_data(self, data):
        try:
            metadata = MetaData()
            metadata.bind = self._engine

            table = Table(self._target_table, metadata, autoload_with=self._engine)
            stmt = (
                insert(table)
                .values(data)
                .on_conflict_do_nothing(index_elements=["keyword", "regist_date", "url"])
            )

            with self._engine.begin() as connection:
                connection.execute(stmt)
        except Exception as error:
            logger.error(error)

    def main(self):
        try:
            keywords = self.get_keywords()
            targets = [
                (keyword, date.strftime("%Y-%m-%d"))
                for keyword in sorted(keywords)
                for date in pd.date_range(self._date_from, self._date_until)
            ]
            for target in targets:
                videos_info = self.get_videos_info(target)
                for video_info in videos_info:
                    self.insert_data(video_info)

        except Exception as error:
            logger.error(error)


if __name__ == "__main__":
    crawler = YoutubeCrawlerTest(
        config=None,
        date_from="2024-04-03",
        date_until="2024-04-03"
    )
    crawler.main()

