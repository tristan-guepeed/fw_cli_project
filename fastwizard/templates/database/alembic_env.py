"""Template pour alembic/env.py"""
def get_template(config):
    return '''import os
import sys
from pathlib import Path
import importlib
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database import Base  # Base partagé pour tous les modèles

# Ajouter le dossier parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Import dynamique de tous les modèles dans app/domains/*
domains_path = Path(__file__).parent.parent / "app" / "domains"
for app_dir in domains_path.iterdir():
    if app_dir.is_dir():
        model_file = app_dir / "model.py"
        if model_file.exists():
            module_name = f"app.domains.{app_dir.name}.model"
            importlib.import_module(module_name)

target_metadata = Base.metadata

# --- configuration Alembic standard ---
config = context.config
if config.config_file_name is not None:
    from logging.config import fileConfig
    fileConfig(config.config_file_name)

# Override DB URL from environment if needed
env_db_url = os.getenv("DATABASE_URL")
if env_db_url:
    config.set_main_option("sqlalchemy.url", env_db_url)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''