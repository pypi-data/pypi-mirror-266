import os
from typing import Any, List, Tuple

import psycopg2
from dotenv import find_dotenv, load_dotenv
from loguru import logger
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import URL, Engine

load_dotenv(dotenv_path=find_dotenv())


def __get_db_info(target: str):
    host = os.environ.get(f"{target}_DB_HOST")
    port = os.environ.get(f"{target}_DB_PORT")
    database = os.environ.get(f"{target}_DB_NAME")
    username = os.environ.get(f"{target}_DB_USERNAME")
    password = os.environ.get(f"{target}_DB_PASSWORD")

    if None in (host, port, database, username, password):
        raise Exception(f"{target}에 대한 환경변수를 제대로 입력해주세요.")

    return host, port, database, username, password


def get_conn(target: str):
    try:
        host, port, database, username, password = __get_db_info(target=target)

        return psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
        )
    except Exception as error:
        logger.error(error)


def get_engine(target: str, drivername: str = "postgresql+psycopg2"):
    try:
        host, port, database, username, password = __get_db_info(target=target)

        dsn = URL.create(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            drivername=drivername,
        )
        return create_engine(dsn)
    except Exception as error:
        logger.error(error)


def create_to_postgres(
    engine: Engine, name: str, *columns: Tuple[Column[Any]], metadata=MetaData()
):
    """
    예시 코드:

    create_to_postgres(
        get_engine("TARGET_DB"),
        "users",
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("age", Integer),
        Column("contact", String),
        UniqueConstraint("name", "contact"),
    )
    """

    try:
        new_table = Table(name, metadata, *columns)
        new_table.create(engine, checkfirst=True)
    except Exception as error:
        logger.error(error)


def insert_to_postgres(
    engine: Engine,
    name: str,
    values: List[dict],
    metadata=MetaData(),
    index_elements=None,
):
    """
    예시 코드:

    users = [
        {"name": "허해준", "age": "29", "contact": "01012345678"},
        {"name": "권재선", "age": "30", "contact": "01087654321"},
    ]
    insert_to_postgres(get_engine("TARGET_DB"), "users", users, index_elements=["name", "contact"])
    """

    try:
        metadata.bind = engine
        table = Table(name, metadata, autoload_with=engine)

        stmt = (
            insert(table)
            .values(values)
            .on_conflict_do_nothing(index_elements=index_elements)
        )

        with engine.begin() as connection:
            connection.execute(stmt)
    except Exception as error:
        logger.error(error)
