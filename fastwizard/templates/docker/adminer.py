"""Template pour Adminer dans docker-compose"""
def get_template(config):
    adminer_port = config.get("adminer_port", 8080)
    
    return f'''
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