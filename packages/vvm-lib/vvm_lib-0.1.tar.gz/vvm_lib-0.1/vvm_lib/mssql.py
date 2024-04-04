import pandas as pd
import pymssql


def select_mssql(sql, conn):
    with pymssql.connect(**conn, as_dict=True) as conn_mssql:
        with conn_mssql.cursor() as mssql_cursor:
            mssql_cursor.execute(sql)
            return pd.DataFrame([row for row in mssql_cursor.fetchall()])
