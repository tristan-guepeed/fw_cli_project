from typing import List

def generate_requirements(module_manager, selected_modules: List[str]) -> str:
    """Génère le fichier requirements.txt"""
    
    base_requirements = [
        "fastapi>=0.121.2",
        "uvicorn[standard]>=0.24.0",
        "python-dotenv>=1.2.1",
        "pydantic-settings>=2.11.0",
    ]
    
    # Ajouter les dépendances des modules
    module_dependencies = module_manager.get_modules_dependencies(selected_modules)
    all_requirements = base_requirements + module_dependencies
    
    # Supprimer les doublons et trier
    unique_requirements = sorted(list(set(all_requirements)))
    
    return "\n".join(unique_requirements)
