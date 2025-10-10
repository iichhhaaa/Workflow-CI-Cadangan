import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === 1️⃣ Load credential dari environment ===
creds_json = os.getenv("GDRIVE_CREDENTIALS")
folder_id = os.getenv("GDRIVE_FOLDER_ID")

if not creds_json or not folder_id:
    raise ValueError("❌ Missing environment variables: GDRIVE_CREDENTIALS or GDRIVE_FOLDER_ID")

creds = json.loads(creds_json)
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# === 2️⃣ Inisialisasi Google Drive API ===
service = build("drive", "v3", credentials=credentials)
print("✅ Connected to Google Drive API.")

# === 3️⃣ Folder Shared Drive Tujuan ===
SHARED_DRIVE_ID = folder_id
print(f"📂 Target Shared Drive Folder ID: {SHARED_DRIVE_ID}")

# === 4️⃣ Fungsi rekursif upload folder ===
def upload_directory(local_dir_path, parent_drive_id):
    """
    Upload folder lokal ke Google Shared Drive secara rekursif.
    """
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)

        if os.path.isdir(item_path):
            folder_meta = {
                "name": item_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_drive_id],
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields="id",
                supportsAllDrives=True
            ).execute()
            new_folder_id = created_folder["id"]
            print(f"📁 Created folder: {item_name} (ID: {new_folder_id})")

            # Rekursif untuk isi folder
            upload_directory(item_path, new_folder_id)

        else:
            print(f"⬆️ Uploading file: {item_name}")
            file_meta = {"name": item_name, "parents": [parent_drive_id]}
            media = MediaFileUpload(item_path, resumable=True)
            uploaded_file = service.files().create(
                body=file_meta,
                media_body=media,
                fields="id",
                supportsAllDrives=True
            ).execute()
            print(f"✅ Uploaded file: {item_name} (ID: {uploaded_file['id']})")


# === 5️⃣ Pastikan folder ./mlruns/0 ada ===
local_mlruns = "./mlruns"
if not os.path.exists(local_mlruns):
    raise FileNotFoundError("❌ Folder ./mlruns tidak ditemukan. Pastikan MLflow sudah dijalankan.")

# === 6️⃣ Buat folder utama 'mlruns' di Shared Drive ===
mlruns_meta = {
    "name": "mlruns",
    "mimeType": "application/vnd.google-apps.folder",
    "parents": [SHARED_DRIVE_ID],
}

mlruns_folder = service.files().create(
    body=mlruns_meta,
    fields="id",
    supportsAllDrives=True
).execute()

mlruns_folder_id = mlruns_folder["id"]
print(f"📁 Created main folder 'mlruns' (ID: {mlruns_folder_id})")

# === 7️⃣ Upload semua isi ./mlruns ke folder mlruns di Drive ===
upload_directory(local_mlruns, mlruns_folder_id)

print("\n🎉 Folder 'mlruns' dan seluruh isinya berhasil diupload ke Shared Drive!")
