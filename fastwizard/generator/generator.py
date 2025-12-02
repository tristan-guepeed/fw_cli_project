"""
Générateur de projets FastAPI
"""
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..modules import ModuleManager

from .submodules.base_structure import create_base_structure
from .submodules.main_files import generate_main_files


console = Console()

class ProjectGenerator:
    """Générateur de projets FastAPI complets"""
    
    def __init__(self):
        self.module_manager = ModuleManager()
        self.templates_dir = Path(__file__).parent.parent / "templates"

    
    # Variables globales pour stocker les configurations
    CRUD_ENTITIES = {}
    DB_CONFIG = {}
    CUSTOM_ROLES = {}
    
    def generate_project(self, project_name: str, selected_modules: List[str]):
        """Génère un projet FastAPI complet"""
        
        # Récupérer les configurations depuis les variables globales
        db_config = getattr(ProjectGenerator, 'DB_CONFIG', {})
        crud_entities = getattr(ProjectGenerator, 'CRUD_ENTITIES', [])
        custom_roles = getattr(ProjectGenerator, 'CUSTOM_ROLES', {})
        
        # Validation des modules
        warnings = self.module_manager.validate_module_combinations(selected_modules)
        if warnings:
            console.print("\n[bold red]❌ Erreurs de configuration des modules :[/bold red]")
            for warning in warnings:
                console.print(f"   [red]• {warning}[/red]")
            console.print()
            raise ValueError("La génération du projet a été annulée en raison des erreurs ci-dessus.")
        
        # Création du répertoire du projet
        project_path = Path(project_name)
        if project_path.exists():
            raise ValueError(f"Le répertoire '{project_name}' existe déjà")
        
        project_path.mkdir()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Structure de base
            task1 = progress.add_task("Création de la structure de base...", total=None)
            create_base_structure(project_path)
            progress.update(task1, completed=True)
            
        # Fichiers principaux
        task2 = progress.add_task("Génération des fichiers principaux...", total=None)
        generate_main_files(
            project_path=project_path,
            project_name=project_name,
            selected_modules=selected_modules,
            db_config=db_config,
            module_manager=self.module_manager,
        )
        progress.update(task2, completed=True)

        # Modules sélectionnés
        if selected_modules:
            task3 = progress.add_task("Génération des modules...", total=None)
            self._generate_modules(project_path, selected_modules)
            progress.update(task3, completed=True)

    def _generate_modules(self, project_path: Path, selected_modules: List[str]):
        """Génère les fichiers des modules sélectionnés"""
        
        for module_id in selected_modules:
            module = self.module_manager.get_module(module_id)

            if module_id == "crud":
                for app_name, config in ProjectGenerator.CRUD_ENTITIES.items():
                    module_dir = project_path / "app" / "domains" / app_name
                    module_dir.mkdir(parents=True, exist_ok=True)
                
                    for file_info in module.files:
                        template_content = self._get_template_content(file_info["template"], {
                            "app_name": app_name,
                            "ModelName": config["ModelName"],
                            "model_name": config["model_name"],
                            "fields": config["fields"],  # <-- ici on passe seulement fields
                            "selected_modules": selected_modules,
                        })
                
                        dest_file_name = file_info["template"].split("/")[-1].replace("_template", "")
                        if dest_file_name == "crud_utils.py":
                            dest_file_name = "router.py"
                
                        file_path = module_dir / dest_file_name
                        file_path.write_text(template_content)
            else:
                for file_info in module.files:
                    file_path = project_path / file_info["path"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    # On construit la config et on y injecte les rôles personnalisés
                    config = {**module.config, "selected_modules": selected_modules}
                    if hasattr(ProjectGenerator, "CUSTOM_ROLES"):
                        config["custom_roles"] = ProjectGenerator.CUSTOM_ROLES.get("roles", [])

                    # Générer le contenu du template
                    template_content = self._get_template_content(file_info["template"], config)   
                    file_path.write_text(template_content)


    
    def _get_template_content(self, template_name: str, config: Dict[str, Any]) -> str:
        """Récupère le contenu d'un template depuis fastwizard/templates"""

        # Chemin vers le dossier templates corrigé
        template_file = self.templates_dir / f"{template_name.replace('.py', '')}.py"

        print(f"Chargement du template: {template_file}")

        if not template_file.exists():
            raise FileNotFoundError(f"Template '{template_name}' introuvable à {template_file}")

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("template_module", template_file)
            template_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_module)

            if hasattr(template_module, "get_template"):
                return template_module.get_template(config)
            else:
                raise AttributeError(
                    f"Le module de template '{template_name}' doit définir une fonction get_template(config)"
                )

        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement du template '{template_name}': {e}")

    