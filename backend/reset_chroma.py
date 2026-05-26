"""
Script pour réinitialiser la base de données ChromaDB
À exécuter quand on modifie data.txt pour forcer la réindexation
"""

import shutil
import os
from loguru import logger

CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

def reset_chromadb():
    """Supprime la base de données ChromaDB pour forcer la réindexation"""
    try:
        if os.path.exists(CHROMA_PERSIST_DIRECTORY):
            shutil.rmtree(CHROMA_PERSIST_DIRECTORY)
            logger.info(f"✅ Base de données ChromaDB supprimée: {CHROMA_PERSIST_DIRECTORY}")
            logger.info("Au prochain démarrage, les données seront réindexées depuis data.txt")
        else:
            logger.info(f"ℹ️ Aucune base de données trouvée à {CHROMA_PERSIST_DIRECTORY}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression: {e}")

if __name__ == "__main__":
    logger.info("🔄 Réinitialisation de la base de données ChromaDB...")
    reset_chromadb()
    logger.info("✅ Terminé! Redémarrez l'application pour réindexer les données.")

# Made with Bob
