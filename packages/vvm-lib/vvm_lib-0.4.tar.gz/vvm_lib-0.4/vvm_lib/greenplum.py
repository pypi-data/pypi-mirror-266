import pandas as pd
import psycopg2
import io
from collections import defaultdict


def select_greenplum(query_sql, connect=None, types=defaultdict(str, A="int", B="float")):
    # with psycopg2.connect(**connect) as postgres_conn:
    #     with postgres_conn.cursor() as postgres_cursor:
    #         output = io.BytesIO()
    #         postgres_cursor.copy_expert(f"COPY ({query_sql}) TO STDOUT (FORMAT 'csv', HEADER true)", output)
    #         output.seek(0)
    # return pd.read_csv(output, engine="python", encoding='utf-8')
    pass


def select_postgres(sql: str, connect: dict) -> pd.DataFrame:
    """
    Функция для select из greenplum и postgres
    :param sql: select * from table;
    :param connect: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :return: DataFrame

    Пример:
        df = select_postgres("select * from table;", connect)
    """
    with psycopg2.connect(**connect) as postgres_conn:
        with postgres_conn.cursor() as postgres_cursor:
            postgres_cursor.execute(sql)
            result = pd.DataFrame(postgres_cursor.fetchall(), columns=[col[0] for col in postgres_cursor.description])
    return result


def postgres_query_read(sql: str, connect: dict, name: str = 'task_1'):
    """
    Функция для выполнения sql запросов не требующих вывода DF в базах greenplum и postgres
    :param sql: drop table table_name;
    :param connect: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :param name: уведомление об окончании запроса
    :return: print(f'Запрос выполнен {name}'

    Пример:
    postgres_query_read('''
            drop table if exists ext_das.das_crm_task;
            CREATE TABLE ext_das.das_crm_task (
            "due_date" DATE,
              "status" TEXT);''', conn, name='das_crm_task')
    """
    with psycopg2.connect(**connect) as postgres_conn:
        with postgres_conn.cursor() as postgres_cursor:
            postgres_cursor.execute(sql)
            postgres_conn.commit()
    print(f'Запрос выполнен {name}')


def insert_greenplum(df: pd.DataFrame, table: str, conn: dict):
    """
    Функция для выполнения insert запросов для баз greenplum и postgres
    :param df: df - который необходимо записать в БД
    :param table: название таблицы "scheme.table"
    :param conn: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :return: уведомление о завершении
    Пример:
        insert_greenplum(total_df, 'scheme.table', conn)
    """
    csv_io = io.StringIO()
    df.to_csv(csv_io, sep='\t', header=False, index=False)
    csv_io.seek(0)
    with psycopg2.connect(**conn) as conn_green:
        with conn_green.cursor() as greenplum:
            greenplum.copy_expert(f"""COPY {table} {str(tuple(df.columns)).replace("'", '"')} FROM STDIN  with (
                                    format csv,delimiter '\t', force_null {str(tuple(df.columns))})""", csv_io)
            conn_green.commit()
    print(f'Данные успешно записаны в {table} объем {len(df)}')
