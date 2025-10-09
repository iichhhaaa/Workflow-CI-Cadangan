# MLProject/upload_to_gdrive.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

def upload_to_gdrive():
    creds_json = os.getenv("GDRIVE_CREDENTIALS")
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not creds_json or not folder_id:
        raise ValueError("Google Drive credentials or folder ID not set!")

    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive.file"])
    service = build("drive", "v3", credentials=creds)

    for root, dirs, files in os.walk("MLProject/mlruns"):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_metadata = {"name": file_name, "parents": [folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"Uploaded {file_name} (ID: {uploaded.get('id')})")

if __name__ == "__main__":
    upload_to_gdrive()
