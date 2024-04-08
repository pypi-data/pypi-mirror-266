import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pandas as pd
from datetime import datetime
from tqdm import tqdm
import pdftotext
from loguru import logger
from dmk_packages.database import database as dbs
from sqlalchemy import MetaData, Table, update


class UpdateFnGuidePdfData:
    """
    다운로드 한 PDF 파일 TEXT 변환 후 UPDATE
    """

    def __init__(self, download_path=None, backup_path=None):
        # 파일 다운로드 경로
        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        # 파일 오류시 백업파일 이동 경로
        self.backup_path = backup_path
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)

        # 데이터베이스
        self.get_engine = dbs.get_engine("KOREAINVESTMENT_DMK")
        self.table_name = "t_fnguide_file_info"

    def update_pdf_data(self):
        logger.info("## PDF 파일 변환 및 적재 시작 ##")
        for file in tqdm(os.listdir(self.download_path)):
            if not file.endswith(".pdf"):
                continue

            # size 0인 파일 삭제후 건너뛰기
            pdf_path = os.path.join(self.download_path, file)
            if os.path.getsize(pdf_path) == 0:
                os.remove(pdf_path)
                continue

            url_idx = file.split("_")[0]
            pdf_path = os.path.join(self.download_path, file)

            # pdf -> text 변환
            with open(pdf_path, "rb") as f:
                pdf = pdftotext.PDF(f)

            pdf_text = ""
            for page in pdf:
                pdf_text += page
            try:
                # db 적재
                logger.info(f"{file} 변환 후 적재")
                metadata = MetaData()
                metadata.bind = self.get_engine
                table = Table(self.table_name, metadata, autoload_with=self.get_engine)

                stmt = (
                    update(table)
                    .where(table.c.url.like(f"%{url_idx}%"))
                    .values(pdf_contents=pdf_text)
                )

                with self.get_engine.begin() as connection:
                    result = connection.execute(stmt)
                    affected_rows = result.rowcount
                if affected_rows == 0:
                    shutil.move(pdf_path, os.path.join(self.backup_path, file))
                    logger.info(f"{file}은 적재할 데이터가 없어 백업폴더로 이동")
                else:
                    os.remove(pdf_path)
            except Exception as error:
                logger.error(f"{file} 적재 오류 : {error}")
        logger.info("## PDF 파일 변환 및 적재 완료 ##")

        # 이관을 위한 스테이터스 테이블 추가
        st = insert_base_status()
        st._insert_fininsh_status(self.table_name)
        logger.info("## 스테이터스 테이블 추가 완료 ##")

    def main(self):
        self.update_pdf_data()


class insert_base_status:
    """
    스테이터스 테이블 추가
    """

    def __init__(self):
        self._dmk_engine = dbs.get_engine("KOREAINVESTMENT_DMK")

    def _insert_fininsh_status(self, table_name):

        df = []
        res = {
            "table_name": str(table_name),
            "started_time": datetime.now(),
            "status_yn": "Y",
            "oracle_status_yn": None,
            "oracle_insert_start_time": None,
            "oracle_insert_end_time": None,
        }
        df.append(res)

        new_df = pd.DataFrame(df)

        new_df.to_sql(
            "t_status_table", self._dmk_engine, index=False, if_exists="append"
        )


if __name__ == "__main__":
    UpdateFnGuidePdfData().main()
