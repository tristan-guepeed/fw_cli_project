# 🧙‍♂️ FastWizard

**FastWizard** est un générateur de projets FastAPI modulaire et interactif qui permet de créer des projets FastAPI complets en choisissant les modules et fonctionnalités souhaités.

## ✨ Fonctionnalités principales

- **🚀 CLI interactive** : Interface utilisateur intuitive avec Rich
- **🔧 Modules réutilisables** : CRUD, Auth, DB, Docker, Tests, etc.
- **📦 Générateur complet** : Structure FastAPI standard + modules choisis
- **🎨 Expérience utilisateur** : Messages clairs, confirmations, progress bars

## 🚀 Installation

### Installation en mode développement

```bash
# Cloner le repository
git clone <repository-url>
cd fw_cli_project

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer en mode développement
pip install -e .
```

## 🎯 Utilisation

### Créer un nouveau projet

```bash
fastwizard new
```

Cette commande lance l'interface interactive qui vous guide à travers :
1. **Nom du projet** : Choisissez un nom pour votre projet
2. **Sélection des modules** : Choisissez les fonctionnalités à inclure
3. **Confirmation** : Vérifiez vos choix avant génération
4. **Génération** : Création automatique du projet

### Commandes disponibles

```bash
# Créer un nouveau projet
fastwizard new

# Lister les modules disponibles
fastwizard modules

# Afficher la version
fastwizard version
```

## 🔧 Modules disponibles

### Base de données
- **`db-postgresql`** : Configuration PostgreSQL avec SQLAlchemy et Alembic

### Authentification
- **A venir**

### Fonctionnalités
- **A venir**

### Développement
- **`docker`** : Dockerfile et docker-compose.yml

## 📁 Structure générée

```
mon-projet-fastapi/
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
├── Dockerfile           # Configuration Docker
├── docker-compose.yml   # Orchestration Docker
├── .env.example         # Variables d'environnement
└── README.md           # Documentation
```

## 🛠️ Développement

### Structure du projet

```
fastwizard/
├── __init__.py          # Point d'entrée
├── cli.py               # Interface CLI principale
├── modules.py           # Gestion des modules
├── generator.py         # Générateur de projets
└── templates/           # Templates de modules
    ├── dockerfile.py
    ├── docker_compose.py
    └── ...
```

### Ajouter un nouveau module

1. **Définir le module** dans `modules.py`
2. **Créer le template** dans `templates/`
3. **Tester** avec `fastwizard new`

## 🧪 Tests

```bash
# Lancer les tests
python test_generation.py

# Test complet avec tous les modules
python test_full_generation.py
```

## 📝 Exemple d'utilisation

```bash
$ fastwizard new

🧙‍♂️ Bienvenue dans FastWizard !
Générateur de projets FastAPI modulaire et interactif
Choisissez vos modules et laissez la magie opérer ! ✨

📝 Quel est le nom de votre projet ? mon-api-fastapi
✨ Projet sélectionné : mon-api-fastapi

🔧 Sélection des modules :
Choisissez les modules à inclure dans votre projet FastAPI

Inclure le module db-postgresql ? [y/n] (n): y
✅ db-postgresql ajouté

Inclure le module docker ? [y/n] (n): y
✅ docker ajouté

📋 Récapitulatif :
   📁 Nom du projet : mon-api-fastapi
   🔧 Modules sélectionnés : 2
      • db-postgresql
      • docker

🚀 Générer le projet avec ces paramètres ? [y/n] (y): y

⠋ Création de la structure de base...

🎉 Projet 'mon-api-fastapi' généré avec succès !
📁 Dossier : /path/to/mon-api-fastapi

🚀 Prochaines étapes :
   cd mon-api-fastapi
   pip install -r requirements.txt
   "Si pas docker :"
   python -m uvicorn main:app --reload
   "Si docker :"
   docker compose up --build
```

## 🙏 Outils

- [FastAPI](https://fastapi.tiangolo.com/)
- [Typer](https://typer.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)

---