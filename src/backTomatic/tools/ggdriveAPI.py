from pathlib import Path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from tqdm import tqdm

import TokenGen.drive_conect as drive_conect

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

BASE_DIR = Path.home().joinpath("Documents", "Backups", "config")
CARPETA_ID_FILE = BASE_DIR / "carpetaID.json"

def guardar_carpeta_id(carpeta_id):
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    with open(CARPETA_ID_FILE, "w", encoding="utf-8") as f:
        json.dump({"carpeta_id": carpeta_id}, f, indent=2)

    print("ID de carpeta guardado")

def obtener_carpeta_backups(service):
    # Primero intenta leer local
    if CARPETA_ID_FILE.exists():
        try:
            with open(CARPETA_ID_FILE, "r", encoding="utf-8") as f:
                carpeta_id = json.load(f).get("carpeta_id")
            
            if carpeta_id:
                # Validar contra Drive
                try:
                    service.files().get(
                        fileId=carpeta_id,
                        fields="id"
                    ).execute()

                    # Si llega aquí, la carpeta existe
                    return carpeta_id

                except Exception:
                    # ID inválido (carpeta borrada en Drive)
                    print("Carpeta guardada ya no existe en Drive, recreando...")
                    CARPETA_ID_FILE.unlink(missing_ok=True)
        except:
            pass

    print("Buscando carpeta Backups en Drive...")

    query = (
        "mimeType='application/vnd.google-apps.folder' "
        "and name='Backups' "
        "and trashed=false"
    )

    resultado = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id,name)"
    ).execute()

    carpetas = resultado.get("files", [])

    if carpetas:
        carpeta_id = carpetas[0]["id"]
        print("Carpeta encontrada")

    else:
        print("No existe Backups — creando carpeta...")

        metadata = {
            "name": "Backups",
            "mimeType": "application/vnd.google-apps.folder"
        }

        carpeta = service.files().create(
            body=metadata,
            fields="id"
        ).execute()

        carpeta_id = carpeta["id"]
        print("Carpeta creada")

    guardar_carpeta_id(carpeta_id)

    return carpeta_id

def subir_zip(zip_path: Path):
    try:
        if not zip_path.exists():
            raise FileNotFoundError(zip_path)
        
        service = drive_conect.conectar_drive()

        carpeta_id = obtener_carpeta_backups(service)

        metadata = {
            "name": zip_path.name,
            "parents": [carpeta_id]
        }

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
