import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from typing import List, Dict, Any
import os
import json
from pathlib import Path

from .modules import ModuleManager
from .generator import ProjectGenerator

console = Console()
app = typer.Typer(
    name="fastwizard",
    help="🧙‍♂️ FastWizard - Générateur de projets FastAPI modulaire et interactif",
    add_completion=False
)

module_manager = ModuleManager()
project_generator = ProjectGenerator()

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
        console.print("\n🚀 [bold]Prochaines étapes :[/bold]")
        console.print(f"   cd {project_name}")
        console.print("   pip install -r requirements.txt")
        console.print("   Sans Docker :")
        console.print("   python -m uvicorn main:app --reload")
        console.print("   Avec Docker :")
        console.print("   docker compose up --build")
        
    except Exception as e:
        console.print(f"❌ [red]Erreur lors de la génération :[/red] {str(e)}")
        raise typer.Exit(1)

def select_modules() -> List[str]:
    """
    Interface interactive pour sélectionner les modules
    """
    console.print("🔧 [bold]Sélection des modules :[/bold]")
    console.print("Choisissez les modules à inclure dans votre projet FastAPI\n")
    
    # Affichage des modules disponibles
    available_modules = module_manager.get_available_modules()
    table = Table(title="Modules disponibles")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Dépendances", style="yellow")
    
    for module_id, module_info in available_modules.items():
        deps = ", ".join(module_info.get("dependencies", []))
        table.add_row(
            module_id,
            module_info.get("description", ""),
            deps if deps else "Aucune"
        )
    
    console.print(table)
    console.print()
    
    selected = []
    for module_id, module_info in available_modules.items():
        if Confirm.ask(f"Inclure le module [bold cyan]{module_id}[/bold cyan] ?", default=False):
            selected.append(module_id)
            console.print(f"✅ [green]{module_id}[/green] ajouté")
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
