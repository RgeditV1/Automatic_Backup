import zipfile
from pathlib import Path

from tqdm import tqdm

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

#**********************AREA DE COMPRESION**********************#

def comprimir_archivo(carpeta_origen: Path, carpeta_destino: Path, 
                      nivel_compresion: int = 1):
    
    if not carpeta_origen.exists() or not carpeta_origen.is_dir():
        print(f"Error: {carpeta_origen} no es una carpeta válida")
        return False
    
    print(f"Comprimiendo: {carpeta_origen.name}")
    
    # Recolectar TODOS los archivos
    archivos = [a for a in carpeta_origen.rglob('*') if a.is_file()]
    
    #aqui eliminaremos algunos archivos que no queremos comprimir
    for i, a in enumerate(archivos):
        if a.suffix in ['.tmp', '.log','.iso']:  # Ejemplo: excluir archivos temporales y logs
            print(f"Excluyendo archivo: {a}")
            archivos.pop(i)

            
    if not archivos:
        print("La carpeta está vacía")
        return False
    
    total_archivos = len(archivos)
    print(f"Total de archivos: {total_archivos}\n")
    
    # Conectar con la función de barra de carga
    return barra_de_carga(archivos, carpeta_origen, carpeta_destino, nivel_compresion)