"""
Système de gestion des modules FastWizard
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class ModuleInfo:
    """Information sur un module"""
    id: str
    name: str
    description: str
    dependencies: List[str]
    files: List[Dict[str, str]]  # Liste des fichiers à générer
    config: Dict[str, Any]  # Configuration du module

class ModuleManager:
    """Gestionnaire des modules disponibles"""
    
    def __init__(self):
        self.modules = self._initialize_modules()
    
    def _initialize_modules(self) -> Dict[str, ModuleInfo]:
        """Initialise tous les modules disponibles"""
        modules = {}
        
        # Module Base de données PostgreSQL
        modules["db-postgresql"] = ModuleInfo(
            id="db-postgresql",
            name="Base de données PostgreSQL",
            description="Configuration PostgreSQL avec SQLAlchemy et Alembic",
            dependencies=["sqlalchemy", "alembic", "psycopg2-binary"],
            files=[
                {
                    "path": "app/database.py",
                    "template": "db_postgresql.py"
                },
                {
                    "path": "alembic.ini",
                    "template": "alembic_ini.py"
                },
                {
                    "path": "alembic/env.py",
                    "template": "alembic_env.py"
                }
            ],
            config={
                "database_url": "postgresql://user:password@localhost/dbname",
                "echo": False
            }
        )
        
        # Module Docker
        modules["docker"] = ModuleInfo(
            id="docker",
            name="Dockerisation",
            description="Configuration Docker avec Dockerfile et docker-compose",
            dependencies=[],
            files=[
                {
                    "path": "Dockerfile",
                    "template": "Dockerfile.py"
                },
                {
                    "path": "docker-compose.yml",
                    "template": "docker_compose.py"
                },
                {
                    "path": ".dockerignore",
                    "template": "dockerignore.py"
                }
            ],
            config={
                "python_version": "3.11",
                "port": 8000,
                "reload": True
            }
        )
        
        return modules
    
    def get_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des modules disponibles"""
        return {
            module_id: {
                "name": module.name,
                "description": module.description,
                "dependencies": module.dependencies,
                "files": module.files,
                "config": module.config
            }
            for module_id, module in self.modules.items()
        }
    
    def get_module(self, module_id: str) -> ModuleInfo:
        """Récupère un module par son ID"""
        if module_id not in self.modules:
            raise ValueError(f"Module '{module_id}' non trouvé")
        return self.modules[module_id]
    
    def get_modules_dependencies(self, module_ids: List[str]) -> List[str]:
        """Récupère toutes les dépendances des modules sélectionnés"""
        dependencies = set()
        for module_id in module_ids:
            module = self.get_module(module_id)
            dependencies.update(module.dependencies)
        return list(dependencies)
    
    def validate_module_combinations(self, module_ids: List[str]) -> List[str]:
        """Valide les combinaisons de modules et retourne les avertissements"""
        warnings = []
        
        # Vérifier les conflits de base de données
        db_modules = [mid for mid in module_ids if mid.startswith("db-")]
        if len(db_modules) > 1:
            warnings.append(f"Conflit détecté : plusieurs modules de base de données sélectionnés ({', '.join(db_modules)})")
        
        # Vérifier les dépendances manquantes
        if "crud" in module_ids and not any(mid.startswith("db-") for mid in module_ids):
            warnings.append("Le module CRUD nécessite un module de base de données")
        
        return warnings