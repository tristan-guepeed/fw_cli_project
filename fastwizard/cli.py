import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.prompt import IntPrompt
from typing import List
import os

from .modules import ModuleManager
from .generator.generator   import ProjectGenerator

console = Console()
app = typer.Typer(
    name="fastwizard",
    help="🧙‍♂️ FastWizard - Générateur de projets FastAPI modulaire et interactif",
    add_completion=False
)

module_manager = ModuleManager()
project_generator = ProjectGenerator()

import subprocess
import re

def check_requirements_updates(requirements_file="requirements.txt"):
    updates_available = []

    with open(requirements_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Extraire nom du package et version si spécifiée
            match = re.match(r"([a-zA-Z0-9_\-\[\]]+)([<>=!~]+[\d\w\.\*]+)?", line)
            if not match:
                continue
            package_name, current_version = match.groups()
            current_version = current_version or ""

            # Vérifier les versions disponibles via pip index
            try:
                result = subprocess.run(
                    ["pip", "index", "versions", package_name],
                    capture_output=True, text=True, check=True
                )
                # pip index versions <pkg> renvoie une ligne contenant la version la plus récente
                available_versions = re.findall(r"Available versions: (.+)", result.stdout)
                if available_versions:
                    latest_version = available_versions[0].split(",")[0].strip()
                    if current_version and latest_version != current_version.lstrip("=<>!~"):
                        updates_available.append(f"{package_name}: {current_version} -> {latest_version}")
            except subprocess.CalledProcessError:
                continue

    return updates_available


@app.command()
def new():
    """
    Crée un nouveau projet FastAPI avec sélection interactive des modules
    """
    # Affichage de bienvenue
    welcome_panel = Panel.fit(
        "[bold cyan]🧙‍♂️ Bienvenue dans FastWizard ![/bold cyan]\n\n"
        "Générateur de projets FastAPI modulaire et interactif\n"
        "Choisissez vos modules et laissez la magie opérer ! ✨",
        border_style="cyan"
    )
    console.print(welcome_panel)
    console.print()

    # Demande du nom du projet
    project_name = Prompt.ask(
        "📝 [bold]Quel est le nom de votre projet ?[/bold]",
        default="mon-projet-fastapi"
    )
    
    # Validation du nom
    if not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("❌ [red]Le nom du projet ne peut contenir que des lettres, chiffres, tirets et underscores[/red]")
        raise typer.Exit(1)

    console.print(f"\n✨ [green]Projet sélectionné :[/green] [bold]{project_name}[/bold]")
    console.print()

    # Sélection des modules
    selected_modules = select_modules()
    
    if not selected_modules:
        console.print("⚠️  [yellow]Aucun module sélectionné. Création d'un projet FastAPI basique.[/yellow]")
        if not Confirm.ask("Continuer ?"):
            raise typer.Exit(0)

    # Confirmation avant génération
    confirm_generation(project_name, selected_modules)
    
    # Génération du projet
    try:
        project_generator.generate_project(project_name, selected_modules)
        console.print(f"\n🎉 [bold green]Projet '{project_name}' généré avec succès ![/bold green]")
        console.print(f"📁 Dossier : [cyan]{os.path.abspath(project_name)}[/cyan]")

        # Exemple d'utilisation juste avant ton "Prochaines étapes"
        updates = check_requirements_updates(os.path.join(project_name, "requirements.txt"))
        if updates:
            console.print("\n⚠️ [bold yellow]Des mises à jour sont disponibles pour certains packages :[/bold yellow]")
            for u in updates:
                console.print(f"  - {u}")
            console.print("⚠️ Attention : mettre à jour ces packages peut casser le projet généré.\n")
        console.print("\n🚀 [bold]Prochaines étapes :[/bold]")
        console.print(f"   cd {project_name}")
        console.print("   pip install -r requirements.txt")
        console.print("   Sans Docker :")
        console.print("   python -m uvicorn main:app --reload")
        console.print("   Avec Docker :")
        console.print("   docker compose up --build")
        console.print("   Avec Makefile :")
        console.print("   make up")
        console.print("   make migrate")

        # si le module linting est présent -> installation pre-commit
        if "linting" in selected_modules:
            console.print("\n🧹 [bold cyan]Linting & Formatting activés[/bold cyan]")
            console.print("    ruff check .")
            console.print("    black .")
        
    except Exception as e:
        console.print(f"❌ [red]Erreur lors de la génération :[/red] {str(e)}")
        raise typer.Exit(1)
    
def prompt_crud_modules():
    """
    Prompt interactif pour générer un ou plusieurs modules CRUD
    Retourne un dictionnaire { app_name: fields }
    """
    crud_modules = {}

    while True:
        console.print("📦 [bold]Configuration d'un module CRUD[/bold]")

        # Nom de l'app
        app_name = Prompt.ask("Nom de l'app (ex: food)").strip()

        # Nombre de champs
        n_fields = int(Prompt.ask("Combien de champs ?", default="1"))

        # Types autorisés
        type_options = ["str", "int", "float", "bool", "datetime"]
        fields = {}

        for i in range(1, n_fields + 1):
            field_name = Prompt.ask(f"Nom du champ {i}").strip()
            while True:
                field_type = Prompt.ask(f"Type du champ {i} ({', '.join(type_options)})").strip()
                if field_type in type_options:
                    break
                console.print(f"⚠️ Type invalide. Choisissez parmi: {', '.join(type_options)}")
            fields[field_name] = field_type

        # Ajouter au dict
        crud_modules[app_name] = fields
        console.print(f"✅ Module CRUD [bold]{app_name}[/bold] configuré avec {len(fields)} champs\n")

        # Demander si l'utilisateur veut en ajouter un autre
        add_another = Confirm.ask("Voulez-vous créer un autre module CRUD ?", default=False)
        if not add_another:
            break

    return crud_modules


def prompt_module_fields():
    app_name = Prompt.ask("Nom de l'app (ex: food)").lower()
    ModelName = Prompt.ask("Nom du modèle (ex: Food)").capitalize()

    fields = {}
    while True:
        field_name = Prompt.ask("Nom du champ (laisser vide pour terminer)", default="").strip()
        if not field_name:
            break
        field_type = Prompt.ask(
            f"Type de '{field_name}'",
            choices=["str", "int", "float", "bool", "datetime"],
            default="str"
        )
        fields[field_name] = field_type
        console.print(f"Champ ajouté : {field_name} ({field_type})")

    return app_name, fields, ModelName


def select_modules() -> List[str]:
    """
    Interface interactive pour sélectionner les modules
    """
    console.print("🔧 [bold]Sélection des modules :[/bold]")
    console.print("Choisissez les modules à inclure dans votre projet FastAPI\n")
    
    available_modules = module_manager.get_available_modules()
    selected = []

    # === 1️⃣ Sélection des bases de données ===
    db_modules = [mid for mid in available_modules if mid.startswith("db-")]

    if db_modules and Confirm.ask("💾 [bold]Souhaitez-vous intégrer une base de données ?[/bold]", default=True):
        console.print("\n📚 [bold cyan]Bases de données disponibles :[/bold cyan]")
        for i, mid in enumerate(db_modules, start=1):
            console.print(f"  {i}. {available_modules[mid]['name']} ({mid})")
        console.print()
        
        choice = IntPrompt.ask(
            "👉 [bold]Choisissez une base de données (numéro)[/bold]",
            choices=[str(i) for i in range(1, len(db_modules) + 1)]
        )
        chosen_db = db_modules[int(choice) - 1]
        selected.append(chosen_db)
        console.print(f"✅ [green]{chosen_db}[/green] ajouté\n")
    else:
        console.print("⏭️  [dim]Aucune base de données sélectionnée[/dim]\n")

    # === 2️⃣ Sélection du système de cache ===
    cache_modules = [mid for mid in available_modules if mid.startswith("cache-")]

    if cache_modules and Confirm.ask("🧠 [bold]Souhaitez-vous intégrer un système de cache ?[/bold]", default=False):
        console.print("\n⚡ [bold cyan]Systèmes de cache disponibles :[/bold cyan]")
        for i, mid in enumerate(cache_modules, start=1):
            console.print(f"  {i}. {available_modules[mid]['name']} ({mid})")
        console.print()

        choice = IntPrompt.ask(
            "👉 [bold]Choisissez un système de cache (numéro)[/bold]",
            choices=[str(i) for i in range(1, len(cache_modules) + 1)]
        )
        chosen_cache = cache_modules[int(choice) - 1]
        selected.append(chosen_cache)
        console.print(f"✅ [green]{chosen_cache}[/green] ajouté\n")
    else:
        console.print("⏭️  [dim]Aucun système de cache sélectionné[/dim]\n")
    
    # === 3️⃣ Sélection du service email ===
    mail_modules = [mid for mid in available_modules if mid.startswith("mail-")]

    if mail_modules and Confirm.ask("✉️ [bold]Souhaitez-vous intégrer un service email ?[/bold]", default=False):
        console.print("\n📧 [bold cyan]Services email disponibles :[/bold cyan]")
        for i, mid in enumerate(mail_modules, start=1):
            console.print(f"  {i}. {available_modules[mid]['name']} ({mid})")
        console.print()

        choice = IntPrompt.ask(
            "👉 [bold]Choisissez un service email (numéro)[/bold]",
            choices=[str(i) for i in range(1, len(mail_modules) + 1)]
        )
        chosen_mail = mail_modules[int(choice) - 1]
        selected.append(chosen_mail)
        console.print(f"✅ [green]{chosen_mail}[/green] ajouté\n")
    else:
        console.print("⏭️  [dim]Aucun service email sélectionné[/dim]\n")

   # === 4️⃣ Sélection du module OAuth2 ===
    oauth_modules = [mid for mid in available_modules if mid.startswith("auth-oauth")]

    if oauth_modules:
        if Confirm.ask("🔐 [bold]Souhaitez-vous intégrer OAuth2 ?[/bold]", default=False):
            console.print("\n🌍 [bold cyan]Providers OAuth disponibles :[/bold cyan]")
            for i, mid in enumerate(oauth_modules, start=1):
                console.print(f"  {i}. {available_modules[mid]['name']} ({mid})")
            console.print()

            choices = Prompt.ask(
                "👉 [bold]Choisissez un ou plusieurs providers OAuth (numéros séparés par des virgules)[/bold]",
                default="",
            )

            if choices:
                for choice in choices.split(","):
                    choice = choice.strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(oauth_modules):
                        chosen_oauth = oauth_modules[int(choice) - 1]
                        if chosen_oauth not in selected:
                            selected.append(chosen_oauth)
                            console.print(f"✅ [green]{chosen_oauth}[/green] ajouté")
                console.print()
            else:
                console.print("⏭️  [dim]Aucun provider OAuth sélectionné[/dim]\n")

    # === 5️⃣ Sélection des autres modules ===
    for module_id, module_info in available_modules.items():
        # ignorer les modules déjà sélectionnés ou appartenant à des catégories spéciales
        if module_id in db_modules or module_id in cache_modules or module_id in mail_modules or module_id in oauth_modules:
            continue

        if Confirm.ask(f"Inclure le module [bold cyan]{module_id}[/bold cyan] ?", default=False):
            selected.append(module_id)
            console.print(f"✅ [green]{module_id}[/green] ajouté")

            # Cas spécial : CRUD
            if module_id == "crud":
                while True:
                    app_name, fields, ModelName = prompt_module_fields()
                    ProjectGenerator.CRUD_ENTITIES[app_name] = {
                        "fields": fields,
                        "ModelName": ModelName,
                        "model_name": app_name.lower(),
                        "app_name": app_name
                    }
                    console.print(f"✅ Module CRUD '{app_name}' configuré\n")

                    if not Confirm.ask("Voulez-vous créer un autre module CRUD ?", default=False):
                        break
        else:
            console.print(f"⏭️  [dim]{module_id}[/dim] ignoré")
        console.print()

    return selected



def confirm_generation(project_name: str, selected_modules: List[str]):
    """
    Confirmation avant génération du projet
    """
    console.print("📋 [bold]Récapitulatif :[/bold]")
    console.print(f"   📁 Nom du projet : [cyan]{project_name}[/cyan]")
    console.print(f"   🔧 Modules sélectionnés : {len(selected_modules)}")
    
    if selected_modules:
        for module in selected_modules:
            console.print(f"      • [green]{module}[/green]")
    else:
        console.print("      • [yellow]Aucun module (projet basique)[/yellow]")
    
    console.print()
    
    if not Confirm.ask("🚀 [bold]Générer le projet avec ces paramètres ?[/bold]", default=True):
        raise typer.Exit(0)

@app.command()
def modules():
    """
    Affiche la liste des modules disponibles
    """
    console.print("🔧 [bold]Modules FastWizard disponibles :[/bold]\n")
    
    available_modules = module_manager.get_available_modules()
    for module_id, module_info in available_modules.items():
        console.print(f"[bold cyan]{module_id}[/bold cyan]")
        console.print(f"  Description: {module_info.get('description', 'N/A')}")
        console.print(f"  Dépendances: {', '.join(module_info.get('dependencies', []))}")
        console.print()

@app.command()
def version():
    """
    Affiche la version de FastWizard
    """
    console.print("🧙‍♂️ [bold cyan]FastWizard v0.1.0[/bold cyan]")

def main():
    """
    Point d'entrée principal de l'application
    """
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Génération annulée par l'utilisateur[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n❌ [red]Erreur inattendue :[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    main()
