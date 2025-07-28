from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sys

def copy_sheet_to_another(spreadsheet_source_id, spreadsheet_target_id, creds_json):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(creds_json, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)

    # 기존 시트들 조회
    target_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_target_id).execute()
    sheets = target_metadata['sheets']

    # server_list 시트가 이미 존재하면 삭제
    for sheet in sheets:
        title = sheet['properties']['title']
        if title == "server_list":
            sheet_id = sheet['properties']['sheetId']
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_target_id,
                body={"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
            ).execute()
            break

    # 소스 시트 ID 얻기
    source_sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_source_id).execute()
    source_sheet_id = source_sheet_metadata['sheets'][0]['properties']['sheetId']

    # 시트 복사
    response = service.spreadsheets().sheets().copyTo(
        spreadsheetId=spreadsheet_source_id,
        sheetId=source_sheet_id,
        body={"destinationSpreadsheetId": spreadsheet_target_id}
    ).execute()
    new_sheet_id = response['sheetId']

    sheet_count = len(service.spreadsheets().get(spreadsheetId=spreadsheet_target_id).execute()['sheets'])

    # 복사한 시트를 마지막 인덱스로 이동
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_target_id,
        body={"requests": [{
            "updateSheetProperties": {
                "properties": {"sheetId": new_sheet_id, "index": sheet_count - 1},
                "fields": "index"
            }
        }]}
    ).execute()

    # 이름을 server_list로 변경
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_target_id,
        body={"requests": [{
            "updateSheetProperties": {
                "properties": {"sheetId": new_sheet_id, "title": "server_list"},
                "fields": "title"
            }
        }]}
    ).execute()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} SOURCE_SPREADSHEET_ID TARGET_SPREADSHEET_ID SERVICE_ACCOUNT_JSON")
        sys.exit(1)
    source_id = sys.argv[1]
    target_id = sys.argv[2]
    json_path = sys.argv[3]
    copy_sheet_to_another(source_id, target_id, json_path)

