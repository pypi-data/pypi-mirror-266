from pathlib import Path
import shutil
import subprocess

def prepare_output_file(output_file, start_file):
    # Příprava výstupního souboru
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write('')

    # Kopírování startovního obsahu
    with open(start_file, 'r') as sf, open(output_file, 'a') as of:
        of.write(sf.read())

def add_directory_structure(APP_DIR, output_file):
    with open(output_file, 'a') as f:
        f.write(f"## Adresářová struktura složky '{APP_DIR}'\n\n")
        if shutil.which('tree'):
            subprocess.run(['tree', APP_DIR], check=True, text=True, stdout=f)
            print("Používám 'tree' pro výpis struktury.")
        else:
            print("'tree' není dostupný. Používám 'find' pro výpis struktury.")
            structure = subprocess.run(['find', APP_DIR, '-print'], capture_output=True, text=True).stdout
            structure = structure.replace(APP_DIR, '').replace('/', '|____')
            f.write(structure)
        f.write('\n')
