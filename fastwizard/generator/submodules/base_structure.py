from pathlib import Path
from rich.console import Console

console = Console()

def create_base_structure(project_path: Path):
    """Crée la structure de base du projet FastAPI"""

    # Répertoires principaux
    directories = [
        "app",
        "app/core",
        "app/middleware",
        "app/domains",
        "tests",
        "logs",
        "alembic",
        "alembic/versions",
    ]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    # Fichiers __init__.py
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/domains/__init__.py",
        "app/middleware/__init__.py",
        "tests/__init__.py",
    ]

    for init_file in init_files:
        (project_path / init_file).touch()

    console.print(f"[green]Structure de base créée dans {project_path}[/green]")
