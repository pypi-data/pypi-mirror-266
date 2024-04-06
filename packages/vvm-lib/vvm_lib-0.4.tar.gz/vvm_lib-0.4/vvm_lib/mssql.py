import pandas as pd
import pymssql


def select_mssql(sql: str, conn: dict) -> pd.DataFrame:
    """
    Функция для select из mssql
    :param sql: select * from table;
    :param conn: {'server': 'master', 'user': f"domen\\{LOGIN}",
               'password': PASSWORD, 'host': 'ms-sql.ru'}
    :return: DataFrame

    Пример:
        df = select_mssql("select * from table;", conn)
    """
    with pymssql.connect(**conn, as_dict=True) as conn_mssql:
        with conn_mssql.cursor() as mssql_cursor:
            mssql_cursor.execute(sql)
            return pd.DataFrame([row for row in mssql_cursor.fetchall()])
