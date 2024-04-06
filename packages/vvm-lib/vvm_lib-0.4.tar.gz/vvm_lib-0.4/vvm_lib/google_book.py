import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_google_sheets(file_id: str, sheet_id: str, accesses: dict) -> pd.DataFrame:
    """
    Функция получает данные из гугл таблицы
    :param file_id: file_id
    :param sheet_id: sheet_id
    :param accesses: accesses - доступы
    :return: DataFrame
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(accesses)
    gc = gspread.authorize(credentials)
    return pd.DataFrame(gc.open_by_key(file_id).get_worksheet_by_id(sheet_id).get_all_records())


def update_worksheet(df: pd.DataFrame, book_id: str, accesses: dict, worksheet_id: str = None
                     , create_new_sheet: bool = False, new_sheet: str = None):
    """
    Функция для записи DataFrame в гугл таблицу
    :param df: DataFrame
    :param book_id: book_id, если записываем на ранее созданный лист, при создании нового не указываем,
        None - по умолчанию
    :param accesses:  accesses - Доступы
    :param worksheet_id:  worksheet_id
    :param create_new_sheet: Если нужно создать новый лист и записать в него, то ставим True, по умолчанию False
    :param new_sheet: Если нужно создать новый лист указываем его имя
    :return:
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(accesses)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(book_id)
    if create_new_sheet:
        worksheet = spreadsheet.add_worksheet(new_sheet, rows=len(df.columns), cols=len(df.columns))
    else:
        worksheet = spreadsheet.get_worksheet_by_id(worksheet_id)
    for i in df.columns:
        df[i] = df[i].astype('str')

    worksheet.update(range_name=f'1:{len(df.columns)}{len(df) + 1}',
                     values=[df.columns.values.tolist()] + df.values.tolist())
    print('Готово')


def clear_worksheet(book_id: str, worksheet_id: str, accesses: dict):
    """
    Функция для удаления всех данных с листа
    :param book_id:  book_id
    :param worksheet_id:  worksheet_id
    :param accesses: accesses
    :return:
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(accesses)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(book_id)
    worksheet = spreadsheet.get_worksheet_by_id(worksheet_id)
    worksheet.clear()
    print(f'Лист {worksheet_id} очищен')
