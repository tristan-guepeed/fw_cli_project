"""Template pour la configuration MySQL"""
def get_template(config):
    database_url = config.get("database_url", "mysql://user:password@localhost/dbname")
    echo = config.get("echo", False)
    
    return f'''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "{database_url}")

# Pour Docker Compose, utiliser le nom du service
if os.getenv("DOCKER_ENV"):
    DATABASE_URL = "mysql://fastapi_user:fastapi_password@db:3306/fastapi_db"

# Créer le moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo={echo},
    pool_pre_ping=True,
    pool_recycle=300,
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
'''