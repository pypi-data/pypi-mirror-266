import subprocess
import shutil
import os
from pathlib import Path
from .ignore_handler import load_ignore_patterns, match_pattern

def add_directory_structure(APP_DIR, output_file):
    ignore_patterns = load_ignore_patterns(os.path.join(APP_DIR, '.turingignore'), APP_DIR)  # Načtení vzorů pro ignorování
    print(os.path.join(APP_DIR, '.turingignore'))
    with open(output_file, 'a') as f:
        f.write(f"## Adresářová struktura složky '{APP_DIR}'\n\n")
        if shutil.which('tree'):
            # Pokud je dostupný 'tree', zatím ignorujeme ignorovací pravidla
            # Alternativně implementujte vlastní logiku pro vytvoření stromové struktury s podporou ignorování
            subprocess.run(['tree', APP_DIR], check=True, text=True, stdout=f)
            print("Používám 'tree' pro výpis struktury.")
        else:
            print("'tree' není dostupný. Používám 'find' pro výpis struktury s ignorováním.")
            # Generování struktury adresářů s podporou ignorování
            for root, dirs, files in os.walk(APP_DIR):
                # Aplikujeme ignorování na adresáře a soubory
                dirs[:] = [d for d in dirs if not match_pattern(os.path.join(root, d), ignore_patterns)]
                files = [f for f in files if not match_pattern(os.path.join(root, f), ignore_patterns)]
                
                # Pro každý neignorovaný soubor nebo adresář přidáme jeho cestu do výstupu
                for name in dirs + files:
                    relative_path = os.path.relpath(os.path.join(root, name), start=APP_DIR)
                    # Vytvoření vizuální reprezentace struktury podobné 'tree'
                    depth = len(relative_path.split(os.sep)) - 1
                    indent = '|   ' * depth
                    f.write(f"{indent}|--- {name}\n")
            f.write('\n')
