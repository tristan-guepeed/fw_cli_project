"""
Générateur de projets FastAPI
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .modules import ModuleManager

console = Console()

class ProjectGenerator:
    """Générateur de projets FastAPI complets"""
    
    def __init__(self):
        self.module_manager = ModuleManager()
        self.templates_dir = Path(__file__).parent / "templates"
    
    # Variables globales pour stocker les configurations
    CRUD_ENTITIES = []
    DB_CONFIG = {}
    
    def generate_project(self, project_name: str, selected_modules: List[str]):
        """Génère un projet FastAPI complet"""
        
        # Récupérer les configurations depuis les variables globales
        db_config = getattr(ProjectGenerator, 'DB_CONFIG', {})
        crud_entities = getattr(ProjectGenerator, 'CRUD_ENTITIES', [])
        
        # Validation des modules
        warnings = self.module_manager.validate_module_combinations(selected_modules)
        if warnings:
            console.print("⚠️  [yellow]Avertissements :[/yellow]")
            for warning in warnings:
                console.print(f"   • {warning}")
            console.print()
        
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
            self._create_base_structure(project_path)
            progress.update(task1, completed=True)
            
        # Fichiers principaux
        task2 = progress.add_task("Génération des fichiers principaux...", total=None)
        self._generate_main_files(project_path, project_name, selected_modules, db_config)
        progress.update(task2, completed=True)
        
        # Modules sélectionnés
        if selected_modules:
            task3 = progress.add_task("Génération des modules...", total=None)
            self._generate_modules(project_path, selected_modules)
            progress.update(task3, completed=True)
            
        # Configuration finale
        task4 = progress.add_task("Configuration finale...", total=None)
        self._finalize_project(project_path, project_name, selected_modules)
        progress.update(task4, completed=True)
    
    def _create_base_structure(self, project_path: Path):
        """Crée la structure de base du projet FastAPI"""
        
        # Répertoires principaux
        directories = [
            "app",
            "app/api",
            "app/api/v1",
            "app/core",
            "app/models",
            "app/schemas",
            "app/routers",
            "app/auth",
            "app/middleware",
            "tests"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
        
        # Fichiers __init__.py
        init_files = [
            "app/__init__.py",
            "app/api/__init__.py",
            "app/api/v1/__init__.py",
            "app/core/__init__.py",
            "app/models/__init__.py",
            "app/schemas/__init__.py",
            "app/routers/__init__.py",
            "app/auth/__init__.py",
            "app/middleware/__init__.py",
            "tests/__init__.py"
        ]
        
        for init_file in init_files:
            (project_path / init_file).touch()
    
    def _generate_main_files(self, project_path: Path, project_name: str, selected_modules: List[str], db_config: dict = None):
        """Génère les fichiers principaux du projet"""
        
        # main.py
        main_content = self._get_main_template(project_name, selected_modules)
        (project_path / "main.py").write_text(main_content)
        
        # requirements.txt
        requirements = self._generate_requirements(selected_modules)
        (project_path / "requirements.txt").write_text(requirements)
        
        # .env.example
        env_content = self._generate_env_example(selected_modules, db_config)
        (project_path / ".env.example").write_text(env_content)
        
        # README.md
        readme_content = self._generate_readme(project_name, selected_modules)
        (project_path / "README.md").write_text(readme_content)
        
        # .gitignore
        gitignore_content = self._get_gitignore_template()
        (project_path / ".gitignore").write_text(gitignore_content)
    
    def _generate_modules(self, project_path: Path, selected_modules: List[str]):
        """Génère les fichiers des modules sélectionnés"""
        
        for module_id in selected_modules:
            module = self.module_manager.get_module(module_id)
            
            for file_info in module.files:
                file_path = project_path / file_info["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Pour l'instant, on crée des fichiers de base
                # Dans une version complète, on utiliserait des templates
                template_content = self._get_template_content(file_info["template"], module.config)
                file_path.write_text(template_content)
    
    def _finalize_project(self, project_path: Path, project_name: str, selected_modules: List[str]):
        """Finalise la configuration du projet"""
        
        # Configuration des modules dans main.py si nécessaire
        if selected_modules:
            self._update_main_with_modules(project_path, selected_modules)
    
    def _get_main_template(self, project_name: str, selected_modules: List[str]) -> str:
        """Template pour main.py"""
        
        imports = ["from fastapi import FastAPI"]
        middleware_setup = []
        router_includes = []
        
        # Ajouter les imports et configurations selon les modules
        if "cors" in selected_modules:
            imports.append("from fastapi.middleware.cors import CORSMiddleware")
            middleware_setup.append("""
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)""")
        
        if "logging" in selected_modules:
            imports.append("from app.core.logging import setup_logging")
            middleware_setup.append("""
# Logging
setup_logging()""")
        
        if "auth-jwt" in selected_modules:
            imports.append("from app.routers.auth import router as auth_router")
            router_includes.append("app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])")
        
        if "file-upload" in selected_modules:
            imports.append("from app.routers.files import router as files_router")
            router_includes.append("app.include_router(files_router, prefix='/api/v1/files', tags=['files'])")
        
        return f'''{chr(10).join(imports)}

app = FastAPI(
    title="{project_name}",
    description="API générée avec FastWizard 🧙‍♂️",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

{chr(10).join(middleware_setup)}

@app.get("/")
async def root():
    return {{"message": "Bienvenue dans {project_name} ! 🚀"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

{chr(10).join(router_includes)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_requirements(self, selected_modules: List[str]) -> str:
        """Génère le fichier requirements.txt"""
        
        base_requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-dotenv>=1.0.0"
        ]
        
        # Ajouter les dépendances des modules
        module_dependencies = self.module_manager.get_modules_dependencies(selected_modules)
        all_requirements = base_requirements + module_dependencies
        
        # Supprimer les doublons et trier
        unique_requirements = sorted(list(set(all_requirements)))
        
        return "\n".join(unique_requirements)
    
    def _generate_env_example(self, selected_modules: List[str], db_config: dict = None) -> str:
        """Génère le fichier .env.example"""
        
        env_vars = [
            "# Configuration de base",
            "APP_NAME=Mon Projet FastAPI",
            "DEBUG=True",
            "SECRET_KEY=your-secret-key-here",
            ""
        ]
        
        # Ajouter les variables selon les modules
        if any(module.startswith("db-") for module in selected_modules) and db_config:
            env_vars.extend([
                "# Base de données",
                f"DATABASE_URL={db_config.get('database_url', 'sqlite:///./app.db')}",
                f"DB_HOST={db_config.get('host', 'localhost')}",
                f"DB_PORT={db_config.get('port', '5432')}",
                f"DB_NAME={db_config.get('database_name', 'fastapi_db')}",
                f"DB_USER={db_config.get('username', 'fastapi_user')}",
                f"DB_PASSWORD={db_config.get('password', 'fastapi_password')}",
                ""
            ])
        
        return "\n".join(env_vars)
    
    def _generate_readme(self, project_name: str, selected_modules: List[str]) -> str:
        """Génère le README.md"""
        
        modules_list = "\n".join([f"- {module}" for module in selected_modules]) if selected_modules else "- Aucun module spécial"
        
        return f'''# {project_name}

Projet FastAPI généré avec [FastWizard](https://github.com/your-repo/fastwizard) 🧙‍♂️

## 🚀 Démarrage rapide

### Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

```

### Lancement

```bash
# Mode développement
python main.py

# Ou avec uvicorn
uvicorn main:app --reload

# Avec Docker
docker compose up --build
```

L'API sera disponible sur [http://localhost:8000](http://localhost:8000)

## 📚 Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔧 Modules inclus

{modules_list}

## 📁 Structure du projet

```
{project_name}/
├── app/
│   ├── api/v1/          # Routes API
│   ├── core/            # Configuration de base
│   ├── models/          # Modèles de données
│   ├── schemas/         # Schémas Pydantic
│   ├── routers/         # Routeurs FastAPI
│   ├── auth/            # Authentification
│   └── middleware/      # Middleware personnalisés
├── tests/               # Tests unitaires
├── main.py              # Point d'entrée
├── requirements.txt     # Dépendances
└── README.md           # Ce fichier
```

## 🛠️ Développement

### Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=app
```

### Base de données

```bash
# Migrations (si Alembic est configuré)
alembic upgrade head

# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"
```

## 📝 Notes

Ce projet a été généré automatiquement avec FastWizard. 
Consultez la documentation de chaque module pour plus d'informations.

---

'''
    
    def _get_gitignore_template(self) -> str:
        """Template pour .gitignore"""
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

'''
    
    def _get_template_content(self, template_name: str, config: Dict[str, Any]) -> str:
        """Récupère le contenu d'un template"""
        
        # Essayer de charger le template depuis un fichier
        template_file = self.templates_dir / f"{template_name.replace('.py', '')}.py"
        
        if template_file.exists():
            try:
                # Charger le module de template
                import importlib.util
                spec = importlib.util.spec_from_file_location("template", template_file)
                template_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(template_module)
                
                # Appeler la fonction get_template du module
                if hasattr(template_module, 'get_template'):
                    return template_module.get_template(config)
                else:
                    raise AttributeError("Template module must have get_template function")
                    
            except Exception as e:
                console.print(f"⚠️  [yellow]Erreur lors du chargement du template {template_name}: {e}[/yellow]")
                return self._get_fallback_template(template_name, config)
        else:
            return self._get_fallback_template(template_name, config)
    
    def _get_fallback_template(self, template_name: str, config: Dict[str, Any]) -> str:
        """Templates de fallback pour les cas où les fichiers de templates n'existent pas"""
        
        if template_name == "Dockerfile.py":
            python_version = config.get("python_version", "3.11")
            port = config.get("port", 8000)
            return f'''FROM python:{python_version}-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
'''
        
        elif template_name == "docker_compose.py":
            port = config.get("port", 8000)
            return f''' 

services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DEBUG=True
    volumes:
      - .:/app
    restart: unless-stopped
    networks:
      - fastapi-network

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: fastapi_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - fastapi-network

volumes:
  postgres_data:

networks:
  fastapi-network:
    driver: bridge
'''
        
        else:
            return f'''# Template: {template_name}
# Configuration: {config}

# TODO: Implémenter le template {template_name}
pass
'''
    
    def _update_main_with_modules(self, project_path: Path, selected_modules: List[str]):
        """Met à jour main.py avec les modules sélectionnés"""
        # Cette méthode pourrait être utilisée pour personnaliser main.py
        # selon les modules sélectionnés
        pass