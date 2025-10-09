import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load Google Drive credentials dari GitHub Secrets
creds = json.loads(os.environ["GDRIVE_CREDENTIALS"])
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build('drive', 'v3', credentials=credentials)
SHARED_DRIVE_ID = os.environ["GDRIVE_FOLDER_ID"]

def upload_directory(local_dir_path, parent_drive_id):
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(item_path):
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()
            new_folder_id = created_folder["id"]
            upload_directory(item_path, new_folder_id)
        else:
            file_meta = {'name': item_name, 'parents': [parent_drive_id]}
            media = MediaFileUpload(item_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

# Sesuaikan path mlruns sesuai struktur repo
# Path folder mlruns
local_mlruns_0 = "./MLProject/mlruns/0"

# Tambahkan pengecekan folder di sini
if not os.path.exists(local_mlruns_0):
    print(f"Folder {local_mlruns_0} tidak ada. Pastikan MLflow sudah dijalankan.")
    exit(1)

# Mulai upload setiap run_id
for run_id in os.listdir(local_mlruns_0):
    run_id_local_path = os.path.join(local_mlruns_0, run_id)
    if os.path.isdir(run_id_local_path):
        run_id_folder_meta = {
            'name': run_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [SHARED_DRIVE_ID]
        }
        run_id_folder = service.files().create(
            body=run_id_folder_meta,
            fields='id',
            supportsAllDrives=True
        ).execute()
        run_id_folder_id = run_id_folder["id"]
        upload_directory(run_id_local_path, run_id_folder_id)

print("=== All MLflow run_id folders uploaded to Google Drive! ===")
