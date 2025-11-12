from typing import List

def get_main_template(project_name: str, selected_modules: List[str]) -> str:
    """Template pour main.py compatible config centralisée et inclusion dynamique des routers"""

    imports = [
        "from fastapi import FastAPI",
        "from contextlib import asynccontextmanager",
    ]
    router_includes = []
    middleware_setup = []

    if "cors" in selected_modules:
        imports.append("from app.core.cors import setup_cors")

    if "auth-jwt" in selected_modules:
        imports.append("from app.domains.auth.router import router as auth_router")
        router_includes.append("app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])")

    if "config" in selected_modules or "cors" in selected_modules:
        imports.append("from app.core.config import get_settings")

    if "logging" in selected_modules:
        imports.append("from app.core.logging import setup_logging")
        imports.append("import logging")

    # === Cache (Redis / Valkey) ===
    if "cache-redis" in selected_modules:
        imports.append("from app.core.cache import lifespan as redis_lifespan")
        lifespan_name = "redis_lifespan"
    elif "cache-valkey" in selected_modules:
        imports.append("from app.core.cache import lifespan as valkey_lifespan")
        lifespan_name = "valkey_lifespan"
    else:
        lifespan_name = None

    # Inclusion du router WebSocket si le module est sélectionné
    if "websocket" in selected_modules:
        imports.append("from app.domains.ws.router import router as ws_router")
        router_includes.append("app.include_router(ws_router, prefix='/ws', tags=['ws'])")

    # Ajouter import pour inclusion dynamique
    imports.append("import importlib")
    imports.append("from pathlib import Path")

    # Startup block
    startup_lines = ["# Startup"]

    if "logging" in selected_modules:
        startup_lines.append("setup_logging()  # Initialisation du logging")
        startup_lines.append("logger = logging.getLogger(__name__)")

    if any(m.startswith("db-") for m in selected_modules):
        startup_lines.append(
            "logger.warning(\"⚠️  Utilisez Alembic pour les migrations (docker compose exec app alembic upgrade head)\")"
        )
    else:
        startup_lines.append("logger.info(\"🚀 Démarrage de l'application\")")

    indent = "    "
    startup_block = "\n".join([indent + line for line in startup_lines])

    # Middleware CORS
    if "cors" in selected_modules:
        middleware_setup.append("settings = get_settings()")
        middleware_setup.append("setup_cors(app)")

    # Inclusion dynamique des routers CRUD
    dynamic_router_code = '''
# Inclusion dynamique de tous les routers CRUD dans app/domains
domains_path = Path(__file__).parent / "app" / "domains"
for domain_dir in domains_path.iterdir():
    if domain_dir.is_dir() and domain_dir.name != "auth":
        try:
            module = importlib.import_module(f"app.domains.{domain_dir.name}.router")
            if hasattr(module, "router"):
                app.include_router(module.router, prefix=f"/api/v1/{domain_dir.name}")
                print(f"✅ Router '{domain_dir.name}' inclus")
        except ModuleNotFoundError:
            print(f"⚠️ Aucun router trouvé pour '{domain_dir.name}'")
            continue
'''

    # Définir le lifespan final
    lifespan_expr = lifespan_name if lifespan_name else "asynccontextmanager(lambda app: (yield))"

    return f'''{chr(10).join(imports)}

@asynccontextmanager
async def lifespan(app):
{startup_block}
    yield
    # Shutdown (si nécessaire)
    print("🛑 Arrêt de l'application")

app = FastAPI(
    title="{project_name}",
    description="API générée avec FastWizard 🧙‍♂️",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan={lifespan_expr}
)

{chr(10).join(middleware_setup)}

@app.get("/")
async def root():
    return {{"message": "Bienvenue dans {project_name} ! 🚀"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

{chr(10).join(router_includes)}

{dynamic_router_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
