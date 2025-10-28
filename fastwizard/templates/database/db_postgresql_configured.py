"""Template PostgreSQL avec configuration personnalisée"""
def get_template(config):
    database_url = config.get("database_url", "postgresql://user:password@localhost/dbname")
    host = config.get("host", "localhost")
    port = config.get("port", "5432")
    database_name = config.get("database_name", "fastapi_db")
    username = config.get("username", "fastapi_user")
    password = config.get("password", "fastapi_password")
    
    return f'''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "{database_url}")
DB_HOST = os.getenv("DB_HOST", "{host}")
DB_PORT = os.getenv("DB_PORT", "{port}")
DB_NAME = os.getenv("DB_NAME", "{database_name}")
DB_USER = os.getenv("DB_USER", "{username}")
DB_PASSWORD = os.getenv("DB_PASSWORD", "{password}")

# Créer le moteur SQLAlchemy avec configuration optimisée
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=300,    # Recycler les connexions après 5 minutes
    pool_size=10,        # Nombre de connexions dans le pool
    max_overflow=20,     # Connexions supplémentaires en cas de besoin
)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crée toutes les tables dans la base de données"""
    Base.metadata.create_all(bind=engine)

def check_connection():
    """Vérifie la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {{e}}")
        return False

# Test de connexion au démarrage
if __name__ == "__main__":
    if check_connection():
        print("✅ Connexion à PostgreSQL réussie !")
        print(f"📊 Base de données: {database_name}")
        print(f"🏠 Hôte: {host}:{port}")
        print(f"👤 Utilisateur: {username}")
    else:
        print("❌ Impossible de se connecter à PostgreSQL")
'''