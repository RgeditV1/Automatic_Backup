from pathlib import Path
import socket
from datetime import datetime

from .compresion import comprimir_archivo
from .ggdriveAPI import subir_zip

TIMEOUT_CONECTION = 5

DOCS_DIR = Path.home() / "Documents"
BACKUP_DIR = DOCS_DIR / "Backups"
CONFIG_DIR = BACKUP_DIR / "config"
VERSIONES_DIR = BACKUP_DIR / "versiones"

DIR_ORIGEN = DOCS_DIR


def is_connected():
    try:
        socket.setdefaulttimeout(TIMEOUT_CONECTION)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print("Conectado a internet")
        return True
    except socket.error:
        print("Verifique su conexión a Internet")
        return False


def asegurar_directorios():
    for d in (BACKUP_DIR, CONFIG_DIR, VERSIONES_DIR):
        d.mkdir(parents=True, exist_ok=True)


def crear_nombre_zip():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return BACKUP_DIR / f"backup_{timestamp}.zip"


def procesar_backup():
    asegurar_directorios()

    save_zip = crear_nombre_zip()

    print("Creando backup...")
    if not comprimir_archivo(DIR_ORIGEN, save_zip):
        print("Error: No se pudo crear el backup")
        return

    print("\n" + "=" * 60)
    print("INICIANDO SUBIDA A GOOGLE DRIVE")
    print("=" * 60)

    resultado = subir_zip(save_zip)

    if resultado:
        print("Backup completado exitosamente")
    else:
        print("\nAdvertencia: No se pudo subir a Google Drive")
        print(f"El backup está guardado localmente en: {save_zip}")


def start():
    if is_connected():
        procesar_backup()
