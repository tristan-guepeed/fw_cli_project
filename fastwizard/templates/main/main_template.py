from typing import List

def get_main_template(project_name: str, selected_modules: List[str]) -> str:
    """Template pour main.py compatible logging + cache + lifespan combiné"""

    imports = [
        "from fastapi import FastAPI",
        "from contextlib import asynccontextmanager",
    ]
    router_includes = []
    middleware_setup = []
    lifespan_name = None
    use_combined_lifespan = False

    # === CORS ===
    if "cors" in selected_modules:
        imports.append("from app.core.cors import setup_cors")

    # === CONFIG ===
    if "config" in selected_modules or "cors" in selected_modules:
        imports.append("from app.core.config import get_settings")

    # === LOGGING ===
    if "logging" in selected_modules:
        imports.append("from app.core.logging import setup_logging")
        imports.append("import logging")

    # === CACHE (redis / valkey) ===
    if "cache-redis" in selected_modules:
        imports.append("from app.core.cache import lifespan as redis_lifespan")
        lifespan_name = "redis_lifespan"
    elif "cache-valkey" in selected_modules:
        imports.append("from app.core.cache import lifespan as valkey_lifespan")
        lifespan_name = "valkey_lifespan"

    # ✅ Determine if we need combined lifespan
    if "logging" in selected_modules and lifespan_name:
        use_combined_lifespan = True

    # === ROUTERS ===
    if "auth-jwt" in selected_modules:
        imports.append("from app.domains.auth.router import router as auth_router")
        router_includes.append("app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])")

    if "websocket" in selected_modules:
        imports.append("from app.domains.ws.router import router as ws_router")
        router_includes.append("app.include_router(ws_router, prefix='/ws', tags=['ws'])")

    if "mail-brevo" in selected_modules:
        imports.append("from app.domains.mails.brevo_router import router as brevo_router")
        router_includes.append("app.include_router(brevo_router, prefix='/api/v1/brevo', tags=['mails'])")

    if "mail-mailjet" in selected_modules:
        imports.append("from app.domains.mails.mailjet_router import router as mailjet_router")
        router_includes.append("app.include_router(mailjet_router, prefix='/api/v1/mailjet', tags=['mails'])")

    if "auth-oauth-google" in selected_modules:
        imports.append("from app.domains.oauth.google.oauth_router import router as google_oauth_router")
        router_includes.append("app.include_router(google_oauth_router, prefix='/api/v1/google_oauth', tags=['google_oauth'])")

    # === Dynamic router loading ===
    imports.append("import importlib")
    imports.append("from pathlib import Path")

    # ✅ Build lifespan block
    lifespan_def = ""

    if use_combined_lifespan:
        lifespan_def = f"""
@asynccontextmanager
async def combined_lifespan(app):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging initialized")

    async with {lifespan_name}(app):
        logger.info("🚀 Application startup complete")
        yield

    logger.info("🛑 Application shutdown")
"""
        lifespan_to_use = "combined_lifespan"

    elif "logging" in selected_modules:
        lifespan_def = """
@asynccontextmanager
async def lifespan(app):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging initialized")
    yield
    logger.info("🛑 Application shutdown")
"""
        lifespan_to_use = "lifespan"

    elif lifespan_name:
        lifespan_to_use = lifespan_name

    else:
        lifespan_to_use = "None"

    # === CORS setup ===
    if "cors" in selected_modules:
        middleware_setup.append("settings = get_settings()")
        middleware_setup.append("setup_cors(app)")

    dynamic_router_code = '''
# Inclusion dynamique de tous les routers CRUD dans app/domains
domains_path = Path(__file__).parent / "app" / "domains"
for domain_dir in domains_path.iterdir():
    if domain_dir.is_dir():
        try:
            module = importlib.import_module(f"app.domains.{domain_dir.name}.router")
            if hasattr(module, "router"):
                app.include_router(module.router, prefix=f"/api/v1/{domain_dir.name}")
                print(f"✅ Router '{domain_dir.name}' inclus")
        except ModuleNotFoundError:
            print(f"⚠️ Aucun router trouvé pour '{domain_dir.name}'")
'''

    return f"""{chr(10).join(imports)}
{lifespan_def}

app = FastAPI(
    title="{project_name}",
    description="API générée avec FastWizard 🧙‍♂️",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan={lifespan_to_use}
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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_config=None, reload=True)
"""
