"""Template pour docker-compose.yml"""
def get_template(config):
    print(config)
    port = config.get("port", 8000)
    adminer_port = config.get("adminer_port", 8080)
    
    # Détecter le type de base de données à partir des modules sélectionnés
    selected_modules = config.get("selected_modules", [])
    db_module = next((m for m in selected_modules if m.startswith("db-")), None)
    
    print(f"Selected DB module: {db_module}")
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

    return f'''
services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DEBUG=True
      - DOCKER_ENV=True
      - DATABASE_URL={database_url}
    volumes:
      - .:/app
    restart: unless-stopped
    depends_on:
      - db
    networks:
      - fastapi-network

  db:
    image: {db_image}
    environment:{db_env}
    volumes:
      - {db_volume}
    ports:
      - "{db_port}:{db_port}"
    networks:
      - fastapi-network

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

volumes:
  {volume_declare}

networks:
  fastapi-network:
    driver: bridge
''' 