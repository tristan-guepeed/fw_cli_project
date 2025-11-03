def get_template(config):
    return '''"""
CORS setup for the FastAPI app
Values are loaded from app.core.config.Settings
"""
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

def setup_cors(app):
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
'''
