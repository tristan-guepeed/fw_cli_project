from typing import List, Optional, Dict

def generate_env_example(selected_modules: List[str], db_config: Optional[Dict] = None) -> str:
        """Génère un fichier .env.example complet et cohérent avec config.py"""

        env_vars = [
            "# ===============================",
            "# 🌐 Configuration de base",
            "# ===============================",
            "APP_NAME=Mon Projet FastAPI",
            "DEBUG=True",
            "ENVIRONMENT=development",
            "",
        ]

        # --- Auth / JWT ---
        if "auth-jwt" in selected_modules:
            env_vars.extend([
                "# ===============================",
                "# 🔐 Configuration JWT",
                "# ===============================",
                "SECRET_KEY=your-super-secret-jwt-key-change-this-in-production",
                "ALGORITHM=HS256",
                "ACCESS_TOKEN_EXPIRE_MINUTES=30",
                "REFRESH_TOKEN_EXPIRE_DAYS=7",
                "",
            ])

        # --- Sécurité / Cookies ---
        if "auth-jwt" in selected_modules or "auth-permissions" in selected_modules:
            env_vars.extend([
                "# ===============================",
                "# 🍪 Cookies & sécurité",
                "# ===============================",
                "COOKIE_SECURE=False",
                "COOKIE_HTTP_ONLY=True",
                "COOKIE_SAME_SITE=lax",
                "",
            ])

        # --- Base de données ---
        if any(module.startswith("db-") for module in selected_modules):
            driver = "postgresql" if "db-postgresql" in selected_modules else "mysql"
            env_vars.extend([
                "# ===============================",
                "# 🗄️ Base de données",
                "# ===============================",
                f"DATABASE_URL={db_config.get('database_url', f'{driver}://user:password@localhost:5432/fastapi_db') if db_config else f'{driver}://user:password@localhost:5432/fastapi_db'}",
                f"DB_HOST={db_config.get('host', 'localhost') if db_config else 'localhost'}",
                f"DB_PORT={db_config.get('port', '5432' if driver == 'postgresql' else '3306') if db_config else ('5432' if driver == 'postgresql' else '3306')}",
                f"DB_NAME={db_config.get('database_name', 'fastapi_db') if db_config else 'fastapi_db'}",
                f"DB_USER={db_config.get('username', 'fastapi_user') if db_config else 'fastapi_user'}",
                f"DB_PASSWORD={db_config.get('password', 'fastapi_password') if db_config else 'fastapi_password'}",
                "",
            ])

        # --- CORS ---
        if "cors" in selected_modules:
            env_vars.extend([
                "# ===============================",
                "# 🌍 Configuration CORS",
                "# ===============================",
                'CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080","http://localhost:4200"]',
                "CORS_ALLOW_CREDENTIALS=True",
                'CORS_ALLOW_METHODS=["*"]',
                'CORS_ALLOW_HEADERS=["*"]',
                "",
            ])

        # --- Docker ---
        if "docker" in selected_modules:
            env_vars.extend([
                "# ===============================",
                "# 🐳 Docker",
                "# ===============================",
                "DOCKER_ENV=production",
                "",
            ])

        # --- Logging ---
        if "logging" in selected_modules:
            env_vars.extend([
                "# ===============================",
                "# 📄 Logging",
                "# ===============================",
                "LOG_LEVEL=INFO",
                "LOG_FORMAT=plain",
                "LOG_FILE=logs/app.log",
                "LOG_MAX_BYTES=5000000",
                "LOG_BACKUP_COUNT=5",
                "",
            ])

        return "\n".join(env_vars)