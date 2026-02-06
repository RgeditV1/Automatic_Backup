# -*- coding: utf-8 -*-

# ------------------------------------------------------------
INFO = {
    "author": "rgeditv1",
    "date": "2024-06-15",
    "version": "Alpha-1.0.2",
    "email": "angelmiguelparedes@gmail.com"
}
# ------------------------------------------------------------

# ------------------------------------------------------------
# Programa de respaldo automático
# Autor: rgeditv1 (https://github.com/rgeditv1)
# Licencia: Este software se distribuye bajo una licencia libre
# que permite usarlo, modificarlo y compartirlo sin restricciones,
# siempre que se mantenga la atribución al autor original.
# ------------------------------------------------------------
import platform
from time import sleep, time
from os import system

from tqdm import tqdm
import tools.backup_proccess as backup_proccess

if platform.system() == "Windows":
    def main():
        for a in INFO:
            print(f"{a.capitalize()}: {INFO[a]}")
        
        sleep(5)
        system("cls")
        
        print("Iniciando proceso de backup automático...\n")
        
        spinner = ["|", "/", "-", "\\"]
        for _ in tqdm(range(50), bar_format="{bar} {postfix}"):
            print(spinner[_ % len(spinner)], end="\r")
            sleep(0.05)
        
        sleep(6)
        system("cls")
        backup_proccess.start()
    if __name__ == "__main__":
        main()
else:
    print("Este programa solo es compatible con Windows.")
