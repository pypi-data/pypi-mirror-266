import os
from pathlib import Path
from .ignore_handler import load_ignore_patterns, match_pattern

def add_file_content(APP_DIR, output_file, file_path):
    relative_path = os.path.relpath(file_path, APP_DIR)
    with open(output_file, 'a') as f:
        f.write(f"# {relative_path}\n\n```\n")
        try:
            # Pokus o otevření a čtení souboru v UTF-8
            with open(file_path, 'r', encoding='utf-8') as content_file:
                f.write(content_file.read())
        except UnicodeDecodeError:
            # Pokud dojde k chybě, pokusíme se otevřít soubor v binárním módu a dekódovat s ignorováním chyb
            with open(file_path, 'rb') as content_file:
                content = content_file.read().decode('utf-8', 'ignore')
                f.write(content)
        f.write('\n```\n\n')

def process_files(APP_DIR, output_file):
    ignore_patterns = load_ignore_patterns(os.path.join(APP_DIR, '.turingignore'),APP_DIR)

    # Zpracování souborů v aplikaci
    for root, dirs, files in os.walk(APP_DIR):
        paths_to_ignore = [os.path.join(root, d) for d in dirs] + [os.path.join(root, f) for f in files]
        dirs[:] = [d for d in dirs if not match_pattern(os.path.join(root, d), ignore_patterns)]  # Modifier pro os.walk
        for file in files:
            file_path = os.path.join(root, file)
            if not match_pattern(file_path, ignore_patterns):
                add_file_content(APP_DIR, output_file, file_path)
