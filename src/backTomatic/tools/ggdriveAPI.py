from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from tqdm import tqdm


SCOPES = ["https://www.googleapis.com/auth/drive.file"]

BASE_DIR = Path.home().joinpath("Documents", "Backups", "config")
TOKEN = BASE_DIR / "token.json"
CREDENTIALS = BASE_DIR / "credentials.json"
CARPETA_ID_FILE = BASE_DIR / "carpetaID.txt"


def obtener_carpeta_id():
    if not CARPETA_ID_FILE.exists():
        return None

    with open (CARPETA_ID_FILE, "r") as f:
        carpeta_id = f.readline()
    return carpeta_id


def conectar_drive():
    creds = None

    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)


def subir_zip(zip_path: Path):
    try:
        if not zip_path.exists():
            raise FileNotFoundError(zip_path)

        if not CREDENTIALS.exists():
            raise FileNotFoundError(CREDENTIALS)

        carpeta_id = obtener_carpeta_id()

        service = conectar_drive()

        metadata = {
            "name": zip_path.name
        }

        if carpeta_id:
            metadata["parents"] = [carpeta_id]

        media = MediaFileUpload(
            str(zip_path),
            resumable=True,
            chunksize=1024 * 1024
        )

        request = service.files().create(
            body=metadata,
            media_body=media,
            fields="id"
        )

        total = zip_path.stat().st_size

        bar = tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            colour="blue",
            desc="Subiendo"
        )

        response = None
        last_progress = 0

        while response is None:
            status, response = request.next_chunk()

            if status:
                current = int(status.progress() * total)
                bar.update(current - last_progress)
                last_progress = current

        bar.close()

        print("\nArchivo subido. ID:", response["id"])
        return True

    except Exception as e:
        print("Error subiendo ZIP:", e)
        return False
