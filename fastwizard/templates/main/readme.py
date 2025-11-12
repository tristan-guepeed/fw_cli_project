from typing import List

def generate_readme(project_name: str, selected_modules: List[str]) -> str:

        """Génère le README.md"""
        
        modules_list = "\n".join([f"- {module}" for module in selected_modules]) if selected_modules else "- Aucun module spécial"
        permissions_section = ''
        if "auth-permissions" in selected_modules:
            permissions_section = '''

## 🔒 Rôles et permissions

Ce projet inclut un système simple de rôles et permissions via `app/core/permissions.py` :

- `require_admin` : restreint l'accès aux administrateurs.
- `require_self_or_admin_by_param` : autorise l'accès si l'utilisateur courant correspond au `user_id` de la route ou est admin.
- `require_self_or_admin_by_owner(owner_id)` : à utiliser après avoir chargé une ressource pour vérifier propriétaire/admin.

Exemples d'utilisation dans une route FastAPI :

```python
from fastapi import APIRouter, Depends
from app.core.permissions import require_admin, require_self_or_admin_by_param

router = APIRouter()

@router.get("/admin-only", dependencies=[Depends(require_admin)])
async def admin_only():
    return {"ok": True}

@router.get("/users/{user_id}", dependencies=[Depends(require_self_or_admin_by_param)])
async def get_user(user_id: int):
    return {"user_id": user_id}
```
'''

        # Logging section
        logging_section = ''
        if "logging" in selected_modules:
            logging_section = '''

## 📄 Logging

Le logging est configuré via `app/core/logging.py`. Les niveaux de log et le format peuvent être ajustés dans ce fichier.

Les logs sont également écrits dans `logs/app.log` (configurable via .env).

Exemple d'utilisation dans une route FastAPI :
```from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.food import services as food_services
from app.domains.food.schemas import Food, FoodCreate, FoodUpdate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foods", tags=["Food"])

@router.get("/", response_model=list[Food])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"📋 Lecture de tous les Foods skip={skip}, limit={limit}")
    foods = food_services.get_food(db, skip=skip, limit=limit)
    logger.info(f"✅ Retour de {len(foods)} Foods")
    return foods
'''

        # Sections explicatives détaillées
        structure_details = '''

## 🧭 Guide de la structure

- `main.py` : Point d'entrée FastAPI. Initialise l'app, CORS (si activé), routes, et lifecycle.
- `app/core/` : Configuration transversale (sécurité, CORS, permissions, etc.).
- `app/domains/` : Dossiers par domaine métier (auth, users, ...). Chaque domaine peut contenir :
  - `model.py` (modèles SQLAlchemy)
  - `schemas.py` (schémas Pydantic)
  - `router.py` (routes FastAPI du domaine)
  - `dependencies.py` (dépendances spécifiques au domaine)
- `app/middleware/` : Middlewares custom.
- `tests/` : Tests unitaires et d'intégration.
- `alembic/` & `alembic.ini` : Migrations DB (si DB activée).
- `Dockerfile` & `docker-compose.yml` : Conteneurisation (si Docker activé).
- `Makefile` : Simplifie les commandes de développement (si Makefile activé).

'''

        cors_section = ''
        if "cors" in selected_modules:
            cors_section = '''

## 🌐 CORS

CORS est activé via `app/core/config.py`. Modifiez origines/méthodes/headers dans ce fichier.

'''

        cache_section = ''
        if "cache-redis" in selected_modules or "cache-valkey" in selected_modules:
            cache_section = '''
## 🗄️ Cache

Le cache est configuré via `app/core/cache.py`. Modifiez les paramètres de connexion dans ce fichier.
'''

        websocket_section = ''
        if "websocket" in selected_modules:
            websocket_section = '''
## 📡 WebSocket

Le module WebSocket est activé. Les routes WebSocket sont définies dans `app/domains/ws/router.py`.
'''

        # Mail module section
        mail_section = ''
        if "mail-brevo" in selected_modules or "mail-mailjet" in selected_modules:
            mail_section = '''
## 📧 Gestion des mails
Le projet inclut un service d'envoi d'emails via
'''
            if "mail-brevo" in selected_modules:
                mail_section += '- Brevo (ex-Sendinblue) via `app/domains/mails/brevo_service.py`\n'
            if "mail-mailjet" in selected_modules:
                mail_section += '- Mailjet via `app/domains/mails/mailjet_service.py`\n'
            mail_section += '''
Configurez les clés API dans le fichier `.env` :
- Pour Brevo : `BREVO_API_KEY`
- Pour Mailjet : `MAILJET_API_KEY` et `MAILJET_API_SECRET`
Utilisez le service mail dans vos routes ou services pour envoyer des emails.
'''

        # Ajouter un rappel migrations dans démarrage rapide si DB active
        migrations_hint = ''
        if any(m.startswith('db-') for m in selected_modules):
            migrations_hint = '\n# Appliquer les migrations (nécessite Alembic configuré)\n# Une migration initiale est créée automatiquement dans alembic/versions/\ndocker compose exec app alembic upgrade head\n'

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
{migrations_hint}

# Avec Makefile
make up
make migrate
```

L'API sera disponible sur [http://localhost:8000](http://localhost:8000)

## 📚 Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Adminer (Base de données)**: [http://localhost:8080](http://localhost:8080)

## 🔧 Modules inclus

{modules_list}

## 🛣️ Routes disponibles

### 🏠 Routes de base

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Page d'accueil |
| `GET` | `/health` | Vérification de l'état de l'API |

### 🔐 Authentification

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|------------------|
| `POST` | `/api/v1/auth/register` | Enregistrement d'un nouvel utilisateur | ✅ |
| `POST` | `/api/v1/auth/login` | Connexion utilisateur | ✅ |
| `POST` | `/api/v1/auth/refresh` | Rafraîchissement du token | ✅ |
| `GET` | `/api/v1/auth/me` | Informations de l'utilisateur actuel | ✅ |
| `PUT` | `/api/v1/auth/me` | Mise à jour du profil utilisateur | ✅ |
| `POST` | `/api/v1/auth/change-password` | Changement de mot de passe | ✅ |
| `GET` | `/api/v1/auth/users` | Liste de tous les utilisateurs | ✅ (Admin) |
| `DELETE` | `/api/v1/auth/users/{{user_id}}` | Suppression d'un utilisateur | ✅ (Admin) |


### 📖 Documentation des routes

Pour une documentation interactive complète :
- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 💡 Exemples d'utilisation

#### Enregistrement d'un utilisateur
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \\
     -H "Content-Type: application/json" \\
     -d '{{"username": "testuser", "email": "test@example.com", "password": "password123"}}'
```

#### Connexion
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
     -H "Content-Type: application/x-www-form-urlencoded" \\
     -d "username=testuser&password=password123"
```

#### Accès à une route protégée
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

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
├── pyproject.toml       # Fichier .toml
├── pre-commit-config.yaml # Fichier .yaml
├── requirements.txt     # Dépendances
└── README.md            # Ce fichier
```

{permissions_section}
{cors_section}
{logging_section}
{structure_details}

## 🛠️ Développement

### Base de données

```bash
# Migrations (si Alembic est configuré)
docker compose exec app alembic upgrade head

# Créer une nouvelle migration
docker compose exec app alembic revision --autogenerate -m "Description"
```

### Visualisation de la base de données

Adminer est inclus pour visualiser et gérer la base de données PostgreSQL ou MySQL.:

1. Accédez à [http://localhost:8080](http://localhost:8080)
2. Utilisez les informations de connexion :
   - **Système** : PostgreSQL/MySQL
   - **Serveur** : db
   - **Utilisateur** : fastapi_user
   - **Mot de passe** : fastapi_password
   - **Base de données** : fastapi_db

## 📝 Notes

Ce projet a été généré automatiquement avec FastWizard. 
Consultez la documentation de chaque module pour plus d'informations.

---

'''