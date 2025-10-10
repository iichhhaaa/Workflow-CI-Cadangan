from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

def upload_to_drive():
    creds_json = os.getenv("GDRIVE_CREDENTIALS")
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not creds_json or not folder_id:
        raise Exception("Missing GDRIVE_CREDENTIALS or GDRIVE_FOLDER_ID")

    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    # Upload file mlruns.zip (hasil training)
    file_name = "mlruns.zip"
    if not os.path.exists(file_name):
        os.system(f"zip -r {file_name} mlruns")

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_name, mimetype="application/zip")

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    print("✅ Upload success to Google Drive!")

if __name__ == "__main__":
    upload_to_drive()
