import pandas as pd
import psycopg2
import io


#Доработать types = defaultdict(str, A="int", B="float")
def select_greenplum(query_sql, connect=None, types=None):
    with psycopg2.connect(**connect) as postgres_conn:
        with postgres_conn.cursor() as postgres_cursor:
            output = io.BytesIO()
            postgres_cursor.copy_expert(f"COPY ({query_sql}) TO STDOUT (FORMAT 'csv', HEADER true)", output)
            output.seek(0)
    return pd.read_csv(output, engine="python", encoding='utf-8')


def select_postgres(sql, connect=None):
    with psycopg2.connect(**connect) as postgres_conn:
        with postgres_conn.cursor() as postgres_cursor:
            postgres_cursor.execute(sql)
            result = pd.DataFrame(postgres_cursor.fetchall(), columns=[col[0] for col in postgres_cursor.description])
    return result


def postgres_query_read(sql, connect=None, name='task_1'):
    with psycopg2.connect(**connect) as postgres_conn:
        with postgres_conn.cursor() as postgres_cursor:
            postgres_cursor.execute(sql)
            postgres_conn.commit()
    print(f'Запрос выполнен {name}')


def insert_greenplum(df, table, conn):
    csv_io = io.StringIO()
    df.to_csv(csv_io, sep='\t', header=False, index=False)
    csv_io.seek(0)
    with psycopg2.connect(**conn) as conn_green:
        with conn_green.cursor() as greenplum:
            greenplum.copy_expert(f"""COPY {table} {str(tuple(df.columns)).replace("'", '"')} FROM STDIN  with (
                                    format csv,delimiter '\t', force_null {str(tuple(df.columns))})""", csv_io)
            conn_green.commit()
    print(f'Данные успешно записаны в {table} объем {len(df)}')