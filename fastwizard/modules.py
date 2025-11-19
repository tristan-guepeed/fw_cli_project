"""
Système de gestion des modules FastWizard
"""
from typing import Dict, List, Any
from dataclasses import dataclass

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
            dependencies=["sqlalchemy==2.0.44", "alembic==1.17.2", "psycopg2-binary==2.9.11"],
            files=[
                {
                    "path": "app/database.py",
                    "template": "database/postgresql/db_postgresql.py"
                },
                {
                    "path": "alembic.ini",
                    "template": "database/alembic_ini.py"
                },
                {
                    "path": "alembic/env.py",
                    "template": "database/alembic_env.py"
                },
                {
                    "path": "alembic/script.py.mako",
                    "template": "database/alembic_script_mako.py"
                }
            ],
            config={
                "database_url": "postgresql://user:password@localhost/dbname",
                "echo": False
            }
        )

        # Module Base de données MySQL
        modules["db-mysql"] = ModuleInfo(
            id="db-mysql",
            name="Base de données MySQL",
            description="Configuration MySQL avec SQLAlchemy et Alembic",
            dependencies=["sqlalchemy==2.0.44", "alembic==1.17.2", "mysqlclient==2.2.7"],
            files=[
                {
                    "path": "app/database.py",
                    "template": "database/mysql/db_mysql.py"
                },
                {
                    "path": "alembic.ini",
                    "template": "database/alembic_ini.py"
                },
                {
                    "path": "alembic/env.py",
                    "template": "database/alembic_env.py"
                },
                {
                    "path": "alembic/script.py.mako",
                    "template": "database/alembic_script_mako.py"
                }
            ],
            config={
                "database_url": "mysql://user:password@localhost/dbname",
                "echo": False
            }
        )
        
        # Module Authentification JWT
        modules["auth-jwt"] = ModuleInfo(
            id="auth-jwt",
            name="Authentification JWT",
            description="Système d'authentification complet avec JWT (register, login, refresh)",
            dependencies=["python-jose[cryptography]==3.5.0", "passlib[bcrypt]==1.7.4", "python-multipart==0.0.20", "email-validator==2.3.0"],
            files=[
                {
                    "path": "app/domains/auth/jwt_handler.py",
                    "template": "auth/auth_jwt_handler.py"
                },
                {
                    "path": "app/domains/auth/dependencies.py",
                    "template": "auth/auth_dependencies.py"
                },
                {
                    "path": "app/domains/auth/model.py",
                    "template": "auth/auth_user_model.py"
                },
                {
                    "path": "app/domains/auth/schemas.py",
                    "template": "auth/auth_schemas.py"
                },
                {
                    "path": "app/domains/auth/router.py",
                    "template": "auth/auth_routes.py"
                },
                {
                    "path": "app/core/security.py",
                    "template": "auth/auth_security.py"
                },
                {
                    "path": "app/core/config.py",
                    "template": "core/config.py"
                },
                {
                    "path": "app/domains/auth/services.py",
                    "template": "auth/auth_services.py"
                }
            ],
            config={
                "secret_key": "your-secret-key-here",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
                "refresh_token_expire_days": 7
            }
        )
        
        # Module Permissions simples (roles user/admin + self-or-admin)
        modules["auth-permissions"] = ModuleInfo(
            id="auth-permissions",
            name="Permissions (rôles simples)",
            description="Dépend de auth-jwt. Fournit des dépendances de permissions: admin requis et self-or-admin.",
            dependencies=[],
            files=[
                {
                    "path": "app/core/permissions.py",
                    "template": "auth/auth_permissions.py"
                }
            ],
            config={}
        )
        
        # Module CORS
        modules["cors"] = ModuleInfo(
            id="cors",
            name="CORS",
            description="Active et configure CORS pour l'API (origines, headers, méthodes).",
            dependencies=[],
            files=[
                {
                    "path": "app/core/cors.py",
                    "template": "core/cors.py"
                }
            ],
            config={
                "origins": ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://localhost:4200"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
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
                    "template": "docker/dockerfile.py"
                },
                {
                    "path": "docker-compose.yml",
                    "template": "docker/docker_compose.py"
                },
                {
                    "path": ".dockerignore",
                    "template": "docker/dockerignore.py"
                }
            ],
            config={
                "python_version": "3.11",
                "port": 8000,
                "reload": True
            }
        )

        modules["makefile"] = ModuleInfo(
            id="makefile",
            name="Makefile",
            description="Fournit un Makefile pour simplifier les commandes de développement",
            dependencies=[],
            files=[],
            config={}
        )

        modules["crud"] = ModuleInfo(
            id="crud",
            name="Générateur CRUD",
            description="Génération de routes CRUD basiques pour les modèles SQLAlchemy",
            dependencies=[],
            files=[
                {"template": "crud/crud_utils.py"},
                {"template": "crud/model_template.py"},
                {"template": "crud/schemas_template.py"},
                {"template": "crud/services_template.py"},
            ],
            config={}
        )

        # Module de linting
        modules["linting"] = ModuleInfo(
            id="linting",
            name="Linting et formatage",
            description="Configuration des outils de linting et formatage (ruff + import sorter)",
            dependencies=["ruff==0.14.5", "black==25.11.0", "pre-commit==4.4.0"],
            files=[
                {
                    "path": "pyproject.toml",
                    "template": "linting/ruff_toml.py"
                },
            ],
            config={}
        )

        modules["logging"] = ModuleInfo(
            id="logging",
            name="Logging",
            description="Configuration des outils de logging (loguru)",
            dependencies=["loguru==0.7.3", "rich==14.2.0"],
            files=[
                {
                    "path": "app/core/logging.py",
                    "template": "core/logging.py"
                }
            ],
            config={}
        )

        # Module Cache Redis
        modules["cache-redis"] = ModuleInfo(
            id="cache-redis",
            name="Cache Redis",
            description="Intégration de Redis pour le cache, les sessions et les tâches en arrière-plan.",
            dependencies=["redis==7.0.1"],
            files=[
                {
                    "path": "app/core/cache.py",
                    "template": "cache/redis_cache.py"
                }
            ],
            config={
                "redis_url": "redis://redis:6379/0"
            }
        )
        
        # Module Cache Valkey (fork open-source de Redis)
        modules["cache-valkey"] = ModuleInfo(
            id="cache-valkey",
            name="Cache Valkey",
            description="Intégration de Valkey (compatible Redis) pour la gestion du cache.",
            dependencies=["redis==7.0.1"],
            files=[
                {
                    "path": "app/core/cache.py",
                    "template": "cache/valkey_cache.py"
                }
            ],
            config={
                "valkey_url": "redis://valkey:6379/0"
            }
        )

        # Module WebSocket (via Starlette / FastAPI)
        modules["websocket"] = ModuleInfo(
            id="websocket",
            name="WebSocket",
            description="Module WebSocket pour FastAPI utilisant Starlette pour la gestion des connexions et rooms.",
            dependencies=[],  # pas besoin de dépendances externes, FastAPI/Starlette suffisent
            files=[
                {
                    "path": "app/core/websocket.py",
                    "template": "websocket/websocket_module.py"
                },
                {
                    "path": "app/domains/ws/router.py",
                    "template": "websocket/websocket_router.py"
                }
            ],
            config={}
        )

        # Module Brevo
        modules["mail-brevo"] = ModuleInfo(
            id="mail-brevo",
            name="Gestion de mails Brevo",
            description="Module d'envoi d'emails via Brevo (ex-Sendinblue)",
            dependencies=["brevo-python==1.2.0", "requests==2.32.5"],
            files=[
                {
                    "path": "app/domains/mails/brevo_service.py",
                    "template": "mails/brevo/brevo_service.py"
                },
                {
                    "path": "app/domains/mails/brevo_router.py",
                    "template": "mails/brevo/brevo_router.py"
                }
            ],
            config={
                "api_key": "YOUR_BREVO_API_KEY",
                "sender_email": "example@example.com",
                "sender_name": "Mon Application"
            }
        )

        # Module Mailjet
        modules["mail-mailjet"] = ModuleInfo(
            id="mail-mailjet",
            name="Gestion de mails Mailjet",
            description="Module d'envoi d'emails via Mailjet",
            dependencies=["mailjet_rest==1.5.1"],
            files=[
                {
                    "path": "app/domains/mails/mailjet_service.py",
                    "template": "mails/mailjet/mailjet_service.py"
                },
                {
                    "path": "app/domains/mails/mailjet_router.py",
                    "template": "mails/mailjet/mailjet_router.py"
                }
            ],
            config={
                "api_key": "YOUR_MAILJET_API_KEY",
                "api_secret": "YOUR_MAILJET_SECRET",
                "sender_email": "example@example.com",
                "sender_name": "Mon Application"
            }
        )

        # Module OAuth Google
        modules["auth-oauth-google"] = ModuleInfo(
            id="auth-oauth-google",
            name="OAuth2 Google",
            description="Module OAuth2 pour Google, permet à l'utilisateur de se connecter via son compte Google.",
            dependencies=["httpx==0.28.1"],
            files=[
                {
                    "path": "app/domains/oauth/oauth_provider.py",
                    "template": "auth/oauth/oauth_provider.py"
                },
                {
                    "path": "app/domains/oauth/oauth_services.py",
                    "template": "auth/oauth/oauth_services.py"
                },
                {
                    "path": "app/domains/oauth/oauth_router.py",
                    "template": "auth/oauth/oauth_router.py"
                }
            ],
            config={
                "provider": "google",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "client_id": "YOUR_GOOGLE_CLIENT_ID",
                "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
                "redirect_uri": "http://localhost:8000/api/v1/oauth/callback"
            }
        )
        

        # Module OAuth GitHub
        #modules["auth-oauth-github"] = ModuleInfo(
        #    id="auth-oauth-github",
        #    name="OAuth2 GitHub",
        #    description="Module OAuth2 pour GitHub, permet à l'utilisateur de se connecter via son compte GitHub.",
        #    dependencies=["httpx", "python-dotenv"],
        #    files=[
        #        {
        #            "path": "app/domains/oauth/oauth_provider.py",
        #            "template": "auth/oauth/oauth_provider.py"
        #        },
        #        {
        #            "path": "app/domains/oauth/oauth_services.py",
        #            "template": "auth/oauth/oauth_services.py"
        #        },
        #        {
        #            "path": "app/domains/oauth/oauth_router.py",
        #            "template": "auth/oauth/oauth_router.py"
        #        }
        #    ],
        #    config={
        #        "provider": "github",
        #        "auth_url": "https://github.com/login/oauth/authorize",
        #        "token_url": "https://github.com/login/oauth/access_token",
        #        "user_info_url": "https://api.github.com/user",
        #        "client_id": "YOUR_GITHUB_CLIENT_ID",
        #        "client_secret": "YOUR_GITHUB_CLIENT_SECRET",
        #        "redirect_uri": "http://localhost:8000/api/v1/oauth/callback"
        #    }
        #)

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
        
        # Vérifier les dépendances manquantes
        #if "crud" in module_ids and not any(mid.startswith("db-") for mid in module_ids):
        #    warnings.append("Le module CRUD nécessite un module de base de données")
        
        if "auth-jwt" in module_ids and not any(mid.startswith("db-") for mid in module_ids):
            warnings.append("LE MODULE AUTH-JWT NECESSITE UN MODULE DE BASE DE DONNEES")
        
        if "auth-permissions" in module_ids and "auth-jwt" not in module_ids:
            warnings.append("LE MODULE AUTH-PERMISSIONS NECESSITE LE MODULE AUTH-JWT")

        if "db-mysql" in module_ids and "db-postgresql" in module_ids:
            warnings.append("CONFLIT DETECTE : LES MODULES DB-MYSQL ET DB-POSTGRESQL NE PEUVENT PAS ETRE UTILISES ENSEMBLE")

        return warnings