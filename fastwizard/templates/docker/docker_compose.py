"""Template pour docker-compose.yml"""
def get_template(config):
    port = config.get("port", 8000)
    adminer_port = config.get("adminer_port", 8080)
    
    # Modules sélectionnés
    selected_modules = config.get("selected_modules", [])
    db_module = next((m for m in selected_modules if m.startswith("db-")), None)
    cache_module = next((m for m in selected_modules if m.startswith("cache-")), None)

    # === Configuration Base de Données ===
    if db_module == "db-mysql":
        db_image = "mysql:8.0"
        db_port = "3306"
        db_volume = "mysql_data:/var/lib/mysql"
        db_env = """
      MYSQL_DATABASE: fastapi_db
      MYSQL_USER: fastapi_user
      MYSQL_PASSWORD: fastapi_password
      MYSQL_ROOT_PASSWORD: rootpassword"""
        database_url = "mysql://fastapi_user:fastapi_password@db:3306/fastapi_db"
        volume_declare = "mysql_data:"
    elif db_module == "db-postgresql":  # Par défaut : PostgreSQL
        db_image = "postgres:15"
        db_port = "5432"
        db_volume = "postgres_data:/var/lib/postgresql/data"
        db_env = """
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: fastapi_password"""
        database_url = "postgresql://fastapi_user:fastapi_password@db:5432/fastapi_db"
        volume_declare = "postgres_data:"
    else:
        db_image = None
        db_port = None
        db_env = ""
        db_volume = ""
        database_url = ""
        volume_declare = ""

    # === Configuration Cache (Redis / Valkey) ===
    cache_service = ""
    cache_dep = ""
    cache_env = ""

    if cache_module == "cache-redis":
        cache_service = f"""
  redis:
    image: redis:7.2
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - fastapi-network
    restart: unless-stopped
"""
        cache_dep = "- redis"
        cache_env = "      - REDIS_URL=redis://redis:6379/0"

    elif cache_module == "cache-valkey":
        cache_service = f"""
  valkey:
    image: valkey/valkey:latest
    container_name: valkey
    ports:
      - "6379:6379"
    volumes:
      - valkey_data:/data
    networks:
      - fastapi-network
    restart: unless-stopped
"""
        cache_dep = "- valkey"
        cache_env = "      - VALKEY_URL=valkey://valkey:6379/0"

    # === Service app ===
    depends = []
    if db_image:
        depends.append("- db")
    if cache_dep:
        depends.append(cache_dep)
    depends_block = "\n      ".join(depends) if depends else ""

    # === Compose final ===
    compose = f'''
services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DEBUG=True
      - DOCKER_ENV=True
      - DATABASE_URL={database_url if database_url else ""}
{cache_env if cache_env else ""}
      - TERM=xterm-256color  # ✅ Force le support des couleurs
      - FORCE_COLOR=1  # ✅ Force les couleurs pour Rich
      - PYTHONUNBUFFERED=1  # ✅ Désactive le buffering pour voir les logs en temps réel
    volumes:
      - .:/app
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      {depends_block}
    networks:
      - fastapi-network
'''

    # === DB Service ===
    if db_image:
        compose += f'''
  db:
    image: {db_image}
    environment:{db_env}
    volumes:
      - {db_volume}
    ports:
      - "{db_port}:{db_port}"
    networks:
      - fastapi-network
'''

    # === Adminer (si DB sélectionnée) ===
    if db_image:
        compose += f'''
  adminer:
    image: adminer:4.8.1
    ports:
      - "{adminer_port}:8080"
    environment:
      ADMINER_DEFAULT_SERVER: db
    depends_on:
      - db
    networks:
      - fastapi-network
    restart: unless-stopped
'''

    # === Cache Service (Redis ou Valkey) ===
    if cache_service:
        compose += cache_service

    # === Volumes et réseau ===
    compose += "\nvolumes:\n"
    compose += "  logs_data:\n"
    if db_image:
        compose += f"  {volume_declare}\n"
    if cache_module == "cache-redis":
        compose += "  redis_data:\n"
    elif cache_module == "cache-valkey":
        compose += "  valkey_data:\n"

    compose += '''
networks:
  fastapi-network:
    driver: bridge
'''
    return compose
