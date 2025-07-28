import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Google Sheets API 버전 및 크레덴셜 파일 설정
api_version = 'v4'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
credentials_file = os.path.join(BASE_DIR, 'auth', 'gifted-veld-307005-27bf7ed08339.json')


# 필터 설정
filter_spec = {
    'filterCriteria': {
        'hiddenValues': ['VM','VMware Virtual Platform','VirtualBox']
    },
    #숨김 설정을 할 인덱스가 위치한 열
    'columnIndex': 12
}

# 첫 번째 열을 정렬하도록 설정 (인덱스 0)
sort_spec = [
    {'dimensionIndex': 14, 'sortOrder': 'DESCENDING'},
    {'dimensionIndex': 0, 'sortOrder': 'ASCENDING'},
]

def create_filter(spreadsheet_id):
    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])

    service = build('sheets', api_version, credentials=credentials)
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']

    # 필터링을 걸 범위를 지정
    request_body = {
        'requests': [
            {
                'setBasicFilter': {
                    'filter': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'startColumnIndex': 0
                        },
                        'sortSpecs': [sort_spec],
                        'filterSpecs': [filter_spec]
                    }
                }
            }
        ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
    response = request.execute()

    print('Filter created successfully.')

if __name__ == '__main__':
    # 스프레드시트 ID는 ansible에서 넘겨 받을 수 있도록 수정
    import sys
    if len(sys.argv) != 2:
        print("Usage: file_filter.py SPREADSHEET_ID")
        sys.exit(1)
    
    spreadsheet_id = sys.argv[1]
    create_filter(spreadsheet_id)
