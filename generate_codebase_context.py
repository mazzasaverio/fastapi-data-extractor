#!/usr/bin/env python3
"""
Script per generare un file di contesto della codebase per LLM
Esclude file non necessari e include solo codice rilevante
"""

import os
import fnmatch
from pathlib import Path
from datetime import datetime

# File e cartelle da escludere
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    "data",
    ".uv-cache",
    "dist",
    "build",
    ".egg-info",
    "docker",
}

EXCLUDE_FILES = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.egg",
    "*.log",
    "*.tmp",
    "*.cache",
    "*.lock",
    "*.pid",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "*.mp3",
    "*.mp4",
    "*.wav",
    "*.avi",
    "*.mov",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
    ".env*",
    ".dockerignore",
    "README.md",
    "generate_codebase_context.py",
    ".gitignore",
    "test_safe_storage.py",
}

# Estensioni di codice da includere
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".sql",
    ".sh",
    ".bash",
    ".dockerfile",
    ".md",
    ".txt",
}

# File specifici da includere sempre (ridotta lista)
ALWAYS_INCLUDE = {
    "LICENSE",
    "Makefile",
    "Dockerfile",
}


def should_exclude_dir(dir_name):
    """Controlla se una directory deve essere esclusa"""
    return dir_name in EXCLUDE_DIRS or (
        dir_name.startswith(".") and dir_name not in ALWAYS_INCLUDE
    )


def should_exclude_file(file_name):
    """Controlla se un file deve essere escluso"""
    # Includi sempre file specifici importanti
    if file_name in ALWAYS_INCLUDE:
        return False

    # Esclude per pattern
    for pattern in EXCLUDE_FILES:
        if fnmatch.fnmatch(file_name.lower(), pattern):
            return True

    # Esclude specifici file per nome esatto
    if file_name in {
        "README.md",
        ".dockerignore",
        "generate_codebase_context.py",
        ".gitignore",
        "test_safe_storage.py",
    }:
        return True

    # Esclude specificamente file .env (controllo aggiuntivo)
    if file_name.startswith(".env"):
        return True

    # Esclude file senza estensione o con estensioni non rilevanti
    file_path = Path(file_name)
    if file_path.suffix and file_path.suffix.lower() not in CODE_EXTENSIONS:
        return True

    # Esclude file specifici ma non importanti
    if file_name.lower() in {"changelog", "authors", "contributors"}:
        return True

    return False


def get_file_content(file_path):
    """Legge il contenuto di un file gestendo encoding diversi"""
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"[ERRORE LETTURA FILE: {str(e)}]"

    return "[IMPOSSIBILE LEGGERE IL FILE - ENCODING NON SUPPORTATO]"


def generate_tree_structure(root_path):
    """Genera la struttura ad albero completa della repository"""
    tree_lines = []

    def add_tree_line(path, prefix="", is_last=True):
        name = os.path.basename(path)
        if name == "":  # root directory
            name = os.path.basename(os.path.abspath(path)) + "/"

        if should_exclude_dir(name) or should_exclude_file(name):
            return

        connector = "└── " if is_last else "├── "
        tree_lines.append(f"{prefix}{connector}{name}")

        if os.path.isdir(path):
            items = []
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if not should_exclude_dir(item) and not should_exclude_file(item):
                        items.append((item, item_path))
            except PermissionError:
                return

            # Ordina: directory prima, poi file, alfabeticamente
            items.sort(key=lambda x: (os.path.isfile(x[1]), x[0].lower()))

            for i, (item_name, item_path) in enumerate(items):
                is_last_item = i == len(items) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                add_tree_line(item_path, new_prefix, is_last_item)

    # Inizia dalla root
    root_name = os.path.basename(os.path.abspath(root_path))
    tree_lines.append(f"{root_name}/")

    # Aggiungi contenuti
    items = []
    try:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if not should_exclude_dir(item) and not should_exclude_file(item):
                items.append((item, item_path))
    except PermissionError:
        pass

    items.sort(key=lambda x: (os.path.isfile(x[1]), x[0].lower()))

    for i, (item_name, item_path) in enumerate(items):
        is_last_item = i == len(items) - 1
        add_tree_line(item_path, "", is_last_item)

    return "\n".join(tree_lines)


def generate_codebase_context(root_path, output_file="codebase_context.txt"):
    """Genera il file di contesto completo della codebase"""

    print(f"🔍 Analizzando la codebase in: {root_path}")
    print(
        "❌ Escludendo: docker/, data/, .gitignore, test_safe_storage.py, README.md, .dockerignore, .env*, cache, logs..."
    )
    print("✅ Includendo: solo codice sorgente e configurazioni essenziali")

    with open(output_file, "w", encoding="utf-8") as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("CODEBASE CONTEXT FOR LLM\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Root Path: {os.path.abspath(root_path)}\n")
        f.write(
            "Excluded: docker/, data/, .gitignore, test_safe_storage.py, README.md, .dockerignore, .env files, cache, logs\n"
        )
        f.write("Included: source code, configuration files (pyproject.toml, etc.)\n")
        f.write("=" * 80 + "\n\n")

        # Project structure - PRIMA COSA
        f.write("📁 REPOSITORY STRUCTURE\n")
        f.write("=" * 50 + "\n")
        f.write("Complete directory tree showing all relevant files and folders:\n\n")
        f.write(generate_tree_structure(root_path))
        f.write("\n\n")
        f.write("=" * 50 + "\n\n")

        # Code files content
        f.write("📄 SOURCE CODE AND CONFIGURATION FILES\n")
        f.write("=" * 50 + "\n\n")

        file_count = 0
        excluded_count = 0

        # Raccogli tutti i file da processare prima
        files_to_process = []

        for root, dirs, files in os.walk(root_path):
            # Filtra le directory
            original_dirs = dirs[:]
            dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
            excluded_count += len(original_dirs) - len(dirs)

            for file in files:
                if should_exclude_file(file):
                    excluded_count += 1
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_path)
                files_to_process.append((file_path, relative_path))

        # Ordina i file: file di configurazione prima, poi per path
        def sort_priority(item):
            file_path, relative_path = item
            filename = os.path.basename(relative_path)

            # Priorità massima per file importanti
            if filename in ["pyproject.toml"]:
                return (0, relative_path)
            # Poi file di configurazione
            elif filename.endswith((".json", ".yaml", ".yml", ".toml", ".ini")):
                return (1, relative_path)
            # Poi file Python
            elif filename.endswith(".py"):
                return (2, relative_path)
            # Resto
            else:
                return (3, relative_path)

        files_to_process.sort(key=sort_priority)

        # Processa i file nell'ordine stabilito
        for file_path, relative_path in files_to_process:
            print(f"📝 Processando: {relative_path}")

            f.write("▼" * 60 + "\n")
            f.write(f"FILE: {relative_path}\n")
            f.write("▼" * 60 + "\n")

            content = get_file_content(file_path)
            f.write(content)
            f.write("\n\n")

            file_count += 1

        # Footer
        f.write("=" * 80 + "\n")
        f.write(f"PROCESSING SUMMARY\n")
        f.write(f"Files included: {file_count}\n")
        f.write(f"Files/directories excluded: {excluded_count}\n")
        f.write(
            f"Repository analyzed: {os.path.basename(os.path.abspath(root_path))}\n"
        )
        f.write("=" * 80 + "\n")

    print(f"✅ Contesto generato in: {output_file}")
    print(f"📊 File inclusi: {file_count}")
    print(f"🚫 File/cartelle esclusi: {excluded_count}")

    # Statistiche dimensioni
    file_size = os.path.getsize(output_file)
    if file_size > 1024 * 1024:
        print(f"📏 Dimensione file: {file_size / (1024 * 1024):.1f} MB")
    else:
        print(f"📏 Dimensione file: {file_size / 1024:.1f} KB")


def main():
    """Funzione principale"""
    root_path = "."
    output_file = "codebase_context.txt"

    if not os.path.exists("pyproject.toml"):
        print("⚠️  Warning: pyproject.toml non trovato. Sei nella directory corretta?")
        response = input("Continuare comunque? (y/N): ")
        if response.lower() != "y":
            return

    print("🚀 Generando contesto codebase...")
    print("📋 Struttura completa della repository sarà mostrata per prima")
    print("🔒 File esclusi:")
    print("   - .gitignore, test_safe_storage.py")
    print("   - README.md, .dockerignore, generate_codebase_context.py")
    print("   - Tutti i file .env*")
    print("   - Cartella docker/ completa")
    print("   - Cartella data/ completa")
    print("   - Cache, logs e file binari")
    print("✅ File inclusi: solo codice sorgente e pyproject.toml")
    print()

    generate_codebase_context(root_path, output_file)

    print(
        f"\n🎉 Completato! Il file '{output_file}' è pronto per essere usato con un LLM."
    )
    print("📁 La struttura completa della repository è mostrata all'inizio del file")


if __name__ == "__main__":
    main()
