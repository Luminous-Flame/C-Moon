import sys
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def find_file(drive_service, folder_id, name):
    query = f"'{folder_id}' in parents and name='{name}' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0] if files else None

def copy_or_get_file(service_account_key, source_file_id, target_name, folder_id):
    credentials = Credentials.from_service_account_file(service_account_key, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build("drive", "v3", credentials=credentials)

    existing_file = find_file(drive_service, folder_id, target_name)
    if existing_file:
        print(existing_file['id'])
        return

    body = {
        'name': target_name,
        'parents': [folder_id]
    }
    copied_file = drive_service.files().copy(fileId=source_file_id, body=body, supportsAllDrives=True).execute()
    print(copied_file['id'])

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: file_copy_check.py <service_account_key> <source_file_id> <target_name> <folder_id>")
        sys.exit(1)
    _, service_account_key, source_file_id, target_name, folder_id = sys.argv
    copy_or_get_file(service_account_key, source_file_id, target_name, folder_id)

