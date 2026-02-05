from pathlib import Path
import socket
from datetime import datetime

from compresion import comprimir_archivo

TIMEOUT_CONECTION = 5

dir = Path.home().joinpath("Documents").resolve()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_zip = Path.home().joinpath("Documents","Backups", f"backup_{timestamp}.zip").resolve()

#Verifica la conexion a internet
def is_connected():
    
    try:
        socket.setdefaulttimeout(TIMEOUT_CONECTION)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print({"status": "connected"})
        return True
    except socket.error as ex:
        print(ex)
        print("Verifique Su Conexion a Internet")
        return False
 
#Revisa los directorios necesarios, encaso de no existir los crea
def check_dirs():
    if not Path.home().joinpath("Documents", "Backups").exists():
        print("No se encontraron los directorios necesarios. Creándolos...")
        make_dirs()
    else:
        print("Directorios Listados.")
        comprimir_archivo(dir, save_zip)
    
def make_dirs():
    backup_dir = Path.home().joinpath("Documents","Backups")
    
    #directorios
    dirs = [
        backup_dir,
        backup_dir /"versiones",    # Historial de versiones
        backup_dir /"config",       # Configuración
    ]
    
    for directorio in dirs:
        directorio.mkdir(parents=True, exist_ok=True)
        print(f"Creado: {directorio}")

def start():
    if is_connected():
        check_dirs()