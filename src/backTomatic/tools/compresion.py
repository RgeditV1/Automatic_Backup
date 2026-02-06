import zipfile
from pathlib import Path
from datetime import datetime
import hashlib

from tqdm import tqdm

EXCLUIR_NOMBRES = {
    "credentials.json",
    "token.json",
    "carpetaID.json",
}

EXCLUIR_SUFFIX = {
    ".tmp",
    ".log",
    ".iso",
    ".lnk",
}

EXCLUIR_RUTAS = set(
    #e.g Path("C:/Users/tu_usuario/AppData"),
)

LOG_EXCLUSIONES = Path.cwd() / "exclusiones.log"

#**********************AREA DE BARRA DE CARGA**********************#
def barra_de_carga(archivos: list, carpeta_origen: Path, archivo_destino: Path, 
                   nivel_compresion: int):
    """
    Muestra barra de carga y comprime los archivos.
    
    Args:
        archivos: Lista de archivos a comprimir
        carpeta_origen: Carpeta origen para rutas relativas
        archivo_destino: Donde guardar el ZIP
        nivel_compresion: Nivel de compresión (0-9)
        
    Returns:
        bool: True si fue exitoso
    """
    total_archivos = len(archivos)
    
    try:
        # Crear ZIP con barra de progreso AZUL
        with zipfile.ZipFile(
            archivo_destino, 
            'w', 
            zipfile.ZIP_DEFLATED, 
            compresslevel=nivel_compresion
        ) as zipf:
            
            # Barra de progreso con color azul
            with tqdm(
                total=total_archivos,
                desc="Comprimiendo",
                unit="archivo",
                colour="blue",
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            ) as barra:
                
                for archivo in archivos:
                    ruta_relativa = archivo.relative_to(carpeta_origen)
                    zipf.write(archivo, ruta_relativa)
                    barra.update(1)
        
        # Barra de "completado" en VERDE
        with tqdm(
            total=1,
            desc="Completado",
            unit="",
            colour="green",
            bar_format='{desc}: {percentage:3.0f}%|{bar}|'
        ) as barra_completado:
            barra_completado.update(1)
        
        # Estadísticas
        tamaño_original = sum(a.stat().st_size for a in archivos)
        tamaño_comprimido = archivo_destino.stat().st_size
        reduccion = (1 - tamaño_comprimido / tamaño_original) * 100
        
        print(f"\nArchivos comprimidos: {total_archivos}")
        print(f"Tamaño original: {tamaño_original / (1024*1024):.2f} MB")
        print(f"Tamaño comprimido: {tamaño_comprimido / (1024*1024):.2f} MB")
        print(f"Reducción: {reduccion:.1f}%")
        print(f"Guardado en: {archivo_destino}")
        
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        return False
    
#**********************AREA DE VALIDACION DE ARCHIVOS**********************#
def archivo_valido(p: Path, vistos: set, excluidos: list) -> bool:
    motivo = None

    # Excluir por ruta
    for ruta in EXCLUIR_RUTAS:
        try:
            if p.resolve().is_relative_to(ruta):
                motivo = "ruta bloqueada"
                break
        except AttributeError:
            # Compatibilidad Python < 3.9
            if str(p.resolve()).startswith(str(ruta)):
                motivo = "ruta bloqueada"
                break

    if not motivo and p.name in EXCLUIR_NOMBRES:
        motivo = "nombre bloqueado"

    elif not motivo and p.suffix.lower() in EXCLUIR_SUFFIX:
        motivo = f"extension bloqueada ({p.suffix})"

    elif not motivo:
        try:
            tamaño = p.stat().st_size
        except Exception:
            motivo = "no se pudo leer tamaño"
        else:
            if tamaño not in vistos:
                vistos[tamaño] = set()

            h = hash_archivo(p)

            if h in vistos[tamaño]:
                motivo = "archivo duplicado por contenido"
            else:
                vistos[tamaño].add(h)


    if motivo:
        excluidos.append((p, motivo))
        return False

    return True

#**********************AREA DE VALIDACION POR HASH**********************#
def hash_archivo(p: Path, chunk=1024 * 1024):
    h = hashlib.sha256()

    with open(p, "rb") as f:
        for bloque in iter(lambda: f.read(chunk), b""):
            h.update(bloque)

    return h.hexdigest()


#**********************AREA DE COMPRESION**********************#

def comprimir_archivo(carpeta_origen: Path, carpeta_destino: Path, 
                      nivel_compresion: int = 1):

    if not carpeta_origen.exists() or not carpeta_origen.is_dir():
        print(f"Error: {carpeta_origen} no es una carpeta válida")
        return False

    print(f"Comprimiendo: {carpeta_origen.name}")

    vistos = {}
    excluidos = []

    # Recolectar todos los archivos
    archivos = [a for a in carpeta_origen.rglob('*') if a.is_file()]

    if not archivos:
        print("La carpeta está vacía")
        return False

    # Filtrar archivos
    archivos_filtrados = [
        a for a in archivos if archivo_valido(a, vistos, excluidos)
    ]

    # Generar log DESPUÉS del filtrado
    if excluidos:
        with open(LOG_EXCLUSIONES, "w", encoding="utf-8") as f:
            f.write(f"Exclusiones - {datetime.now()}\n\n")

            for p, motivo in excluidos:
                f.write(f"{p} -> {motivo}\n")

        print(f"\nSe excluyeron {len(excluidos)} archivos.")
        print(f"Log generado en: {LOG_EXCLUSIONES.resolve()}")

    else:
        print("\nNo hubo archivos excluidos.")

    print(f"Total de archivos incluidos: {len(archivos_filtrados)}\n")

    # Comprimir SOLO los filtrados
    return barra_de_carga(
        archivos_filtrados,
        carpeta_origen,
        carpeta_destino,
        nivel_compresion
    )
