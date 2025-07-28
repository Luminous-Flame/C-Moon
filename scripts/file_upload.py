import argparse
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload

def upload_spreadsheet_to_drive(service_account_key, spreadsheet_path, drive_folder_id):
    credentials = Credentials.from_service_account_file(service_account_key, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": os.path.basename(spreadsheet_path),
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [drive_folder_id]
    }

    media = MediaFileUpload(
        spreadsheet_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d")
    filename, extension = os.path.splitext(file_metadata["name"])
    new_filename = f"{filename}_{timestamp}{extension}"
    file_metadata["name"] = new_filename

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()
    file_id = file.get('id')

    print(f"{file.get('id')}")
    return file_id

def main():
    parser = argparse.ArgumentParser(description="Upload spreadsheet to Google Drive")
    parser.add_argument("--service-account-key", help="Path to the service account key JSON file", required=True)
    parser.add_argument("--spreadsheet-path", help="Path to the spreadsheet file to upload", required=True)
    parser.add_argument("--drive-folder-id", help="ID of the folder in Google Drive to upload the spreadsheet to", required=True)
    args = parser.parse_args()

    upload_spreadsheet_to_drive(args.service_account_key, args.spreadsheet_path, args.drive_folder_id)

if __name__ == "__main__":
    main()
