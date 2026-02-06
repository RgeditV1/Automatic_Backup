from pathlib import Path
from sys import exit
import socket
from msvcrt import getch

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Carpeta config
CONFIG_DIR = Path.home() / "Documents" / "Backups" / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Archivos
TOKEN = CONFIG_DIR / "token.json"
CREDENTIALS = CONFIG_DIR / "credentials.json"

TIMEOUT_CONECTION = 5

def is_connected():
    try:
        socket.setdefaulttimeout(TIMEOUT_CONECTION)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print("Conectado a internet")
        return True
    except socket.error:
        print("Verifique su conexión a Internet")
        return False


def conectar_drive():
    if not CREDENTIALS.exists():
        print("\nERROR: No se encontró credentials.json")
        print("Debe colocar su archivo credentials.json en:")
        print(CONFIG_DIR)
        print("\n Si ya tiene el archivo, asegúrese de que se llame exactamente 'credentials.json'y esté en la ubicación correcta.")
        print("\n Consulte con el desarrollador para obtener ayuda.\n")
        
        print("intentar de nuevo...")
        getch()

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

        TOKEN.write_text(creds.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=creds)
