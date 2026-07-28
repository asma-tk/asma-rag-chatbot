# Utilise une image Python stable où tout est déjà configuré
FROM python:3.11-slim

# Évite que Python écrive des fichiers .pyc et force l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installer les dépendances système nécessaires pour compiler pydantic-core
# Ajout de rust et cargo pour la compilation de pydantic-core
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . $HOME/.cargo/env \
    && rm -rf /var/lib/apt/lists/*

# Ajouter Rust au PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copier et installer les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Pré-télécharger le modèle d'embeddings DANS l'image (87 Mo) ---
# Sans ça, initialize_embeddings() retéléchargeait all-MiniLM-L6-v2 depuis
# HuggingFace à CHAQUE démarrage à froid, car le disque de Render est éphémère.
# C'était la cause principale des >2 min de démarrage : le premier visiteur
# après une période d'inactivité n'obtenait jamais de réponse.
#
# HF_HOME doit rester défini au runtime (ENV, pas ARG) pour que le cache soit
# retrouvé. HF_HUB_OFFLINE=1 évite tout appel réseau de vérification au
# démarrage — testé : le modèle se charge hors ligne en ~1,7 s.
ENV HF_HOME=/opt/hf-cache
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# APRÈS le téléchargement seulement : ENV s'applique aussi aux étapes de build
# suivantes, donc activer le mode hors ligne plus haut ferait échouer le RUN
# ci-dessus.
ENV HF_HUB_OFFLINE=1

# Copier le reste du projet
# Placé APRÈS le modèle : modifier app.py ou data.txt ne réinvalide pas
# la couche de 87 Mo, donc les redéploiements restent rapides.
COPY . .

# Exposer le port (Render utilise une variable d'environnement $PORT)
EXPOSE $PORT

# Commande de démarrage (Uvicorn avec port dynamique)
# Render fournit automatiquement la variable d'environnement PORT
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}