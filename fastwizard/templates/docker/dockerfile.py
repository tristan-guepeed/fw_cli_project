"""Template pour Dockerfile"""

def get_template(config):
    python_version = config.get("python_version", "3.11")
    port = config.get("port", 8000)
    
    return f'''FROM python:{python_version}-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer le port
EXPOSE {port}

# Commande par défaut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
'''