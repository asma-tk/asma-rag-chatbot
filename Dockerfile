# Utilise une image Python stable où tout est déjà configuré
FROM python:3.11-slim

# Évite que Python écrive des fichiers .pyc et force l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installer les dépendances système si nécessaire
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

# Copier et installer les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# Exposer le port (Render utilise une variable d'environnement $PORT)
EXPOSE $PORT

# Commande de démarrage (Uvicorn avec port dynamique)
# Render fournit automatiquement la variable d'environnement PORT
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}