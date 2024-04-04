import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_google_sheets(file_id, sheet_id, accesses):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(accesses)
    gc = gspread.authorize(credentials)
    return pd.DataFrame(gc.open_by_key(file_id).get_worksheet_by_id(sheet_id).get_all_records())


def update_worksheet(df, book_id, accesses, worksheet_id=None, create_new_sheet=False, new_sheet=None):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(accesses)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(book_id)
    if create_new_sheet:
        worksheet = spreadsheet.add_worksheet(new_sheet, rows=len(df.columns), cols=len(df.columns))
    else:
        worksheet = spreadsheet.get_worksheet_by_id(worksheet_id)
    for i in df.columns:
        df[i] = df[i].astype('str')
        
    worksheet.update(range_name=f'1:{len(df.columns)}{len(df)+1}', 
                            values=[df.columns.values.tolist()] + df.values.tolist())
    print('Готово')
