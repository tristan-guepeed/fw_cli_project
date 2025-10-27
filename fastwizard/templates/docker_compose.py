"""Template pour docker-compose.yml"""
def get_template(config):
    port = config.get("port", 8000)
    
    return f'''

services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - DEBUG=True
    volumes:
      - .:/app
      - ./logs:/app/logs
      - ./uploads:/app/uploads
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

volumes:
  postgres_data:

networks:
  fastapi-network:
    driver: bridge
'''