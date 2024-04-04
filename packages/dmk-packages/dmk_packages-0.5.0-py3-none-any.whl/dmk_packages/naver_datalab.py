import pandas as pd
from sqlalchemy import text


def reset_key_active(engine):
    try:
        query = """
                UPDATE t_auth_naver_datalab_key_v2
                SET is_active          = FALSE,
                    failed_active_date = NULL
                WHERE NOT is_active
                  AND failed_active_date < CURRENT_DATE;
                """

        with engine.begin() as connection:
            connection.execute(text(query))

        return True
    except Exception as error:
        raise Exception(error)


def get_key(engine):
    try:
        if engine is None:
            raise Exception("마대리 인증 정보 DB에 접근할 수 없습니다.")

        reset_key_active(engine)

        query = """
              SELECT id, client_id, client_secret
              FROM t_auth_naver_datalab_key_v2
              WHERE is_active
                AND is_auth
              ORDER BY RANDOM()
              LIMIT 1;
              """
        df = pd.read_sql(query, engine)

        if df.empty:
            return None, None, None

        return df.loc[0, "id"], df.loc[0, "client_id"], df.loc[0, "client_secret"]
    except Exception as error:
        raise Exception(error)


def update_key(pk_id, feather, engine):
    try:
        if engine is None:
            raise Exception("마대리 인증 정보 DB에 접근할 수 없습니다.")

        if feather not in ["auth", "active"]:
            raise Exception("사용할 수 없는 feather입니다.")

        query = f"""
                UPDATE t_auth_naver_datalab_key_v2
                SET is_{feather} = FALSE,
                    failed_{feather}_date = CURRENT_DATE
                WHERE id = {pk_id}
                """

        with engine.begin() as connection:
            connection.execute(text(query))

        return True
    except Exception as error:
        raise Exception(error)
