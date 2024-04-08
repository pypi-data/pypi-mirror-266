import os
import fnmatch

def load_ignore_patterns(ignore_file_path, APP_DIR):
    """Načte vzory pro ignorování ze souboru a vrátí je jako seznam."""
    patterns = []
    try:
        with open(ignore_file_path, 'r') as file:
            for line in file:
                # Odstranění bílých znaků na začátku/konci a ignorování prázdných řádků a komentářů
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    ignore_path=os.path.join(APP_DIR, stripped_line)
                    patterns.append(ignore_path)
    except FileNotFoundError:
        print(f"Upozornění: Soubor pro ignorování {ignore_file_path} nebyl nalezen. Ignorovací vzory nebudou aplikovány.")
    return patterns

def match_pattern(path, ignore_patterns):
    """Vrátí True, pokud by cesta měla být ignorována na základě seznamu vzorů."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            print(path)
            return True
    return False
