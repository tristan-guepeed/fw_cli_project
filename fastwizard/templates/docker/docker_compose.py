"""Template pour docker-compose.yml"""
def get_template(config):
    port = config.get("port", 8000)
    adminer_port = config.get("adminer_port", 8080)
    
    return f'''

services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DEBUG=True
      - DOCKER_ENV=True
      - DATABASE_URL=postgresql://fastapi_user:fastapi_password@db:5432/fastapi_db
    volumes:
      - .:/app
    restart: unless-stopped
    depends_on:
      - db
    networks:
      - fastapi-network

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: fastapi_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
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
  postgres_data:

networks:
  fastapi-network:
    driver: bridge
'''