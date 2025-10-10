from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json
import sys

def upload_to_drive():
    # Ambil credentials dan folder ID dari environment (GitHub Secrets)
    creds_json = os.getenv("GDRIVE_CREDENTIALS")
    folder_id = os.getenv("GDRIVE_FOLDER_ID")

    if not creds_json or not folder_id:
        print("❌ ERROR: Missing environment variables GDRIVE_CREDENTIALS or GDRIVE_FOLDER_ID")
        sys.exit(1)

    # Parsing JSON credentials
    try:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    except Exception as e:
        print("❌ ERROR: Invalid service account credentials.")
        print(str(e))
        sys.exit(1)

    # Inisialisasi service Google Drive
    try:
        drive_service = build("drive", "v3", credentials=creds)
    except Exception as e:
        print("❌ ERROR: Gagal menginisialisasi Google Drive API.")
        print(str(e))
        sys.exit(1)

    # Tentukan file yang mau diupload
    file_name = "mlruns.zip"

    # Jika belum ada zip-nya, buat otomatis
    if not os.path.exists(file_name):
        print("📦 File mlruns.zip belum ada — membuat zip dari folder ./mlruns ...")
        os.system("zip -r mlruns.zip mlruns || echo '⚠️ Folder mlruns tidak ditemukan, membuat dummy file.'")
        if not os.path.exists(file_name):
            with open(file_name, "w") as f:
                f.write("No mlruns folder found. Dummy file created.")

    # Siapkan metadata file untuk upload ke Shared Drive
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }

    media = MediaFileUpload(file_name, mimetype="application/zip", resumable=True)

    print("☁️ Uploading file to Google Shared Drive...")

    try:
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, parents",
            supportsAllDrives=True  # penting untuk Shared Drive!
        ).execute()

        print(f"✅ Upload sukses! File ID: {uploaded['id']} | Nama: {uploaded['name']}")
    except Exception as e:
        print("❌ ERROR saat upload ke Google Drive:")
        print(str(e))
        sys.exit(1)

if __name__ == "__main__":
    upload_to_drive()
