#!/bin/bash

# Script de démarrage du chatbot Asma Taberkokt
# Usage: ./start.sh

echo "🚀Démarrage du chatbot Asma Taberkokt..."
echo ""

# Vérifier si le venv existe
if [ ! -d "venv" ]; then
    echo "Environnement virtuel non trouvé."
    echo "Créez-le avec: python3 -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo " Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si Ollama est en cours d'exécution
echo " Vérification d'Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  Ollama n'est pas démarré."
    echo "Démarrez-le avec: ollama serve"
    echo ""
    read -p "Voulez-vous continuer quand même ? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Ollama est en cours d'exécution"
fi

# Vérifier si le modèle phi3 est installé
echo " Vérification du modèle phi3..."
if ! ollama list | grep -q "phi3"; then
    echo "⚠️  Le modèle phi3 n'est pas installé."
    echo "Installez-le avec: ollama pull phi3"
    echo ""
    read -p "Voulez-vous l'installer maintenant ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull phi3
    else
        exit 1
    fi
else
    echo "Modèle phi3 disponible"
fi

# Démarrer l'application
echo ""
echo "🎯 Démarrage du serveur FastAPI..."
echo "📍 URL: http://localhost:8000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 app.py

# Made with Bob
