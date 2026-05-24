# Chatbot Personnel RAG - Asma Taberkokt

Un chatbot intelligent utilisant la technologie RAG (Retrieval-Augmented Generation) pour répondre aux questions sur Asma Taberkokt, développeuse IA passionnée.

## Architecture RAG

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUX RAG COMPLET                         │
└─────────────────────────────────────────────────────────────┘

    📄 Documents (data.txt)
           ↓
    ✂️  Chunking (RecursiveCharacterTextSplitter)
           ↓
    🧮 Embeddings (Sentence Transformers)
           ↓
    💾 ChromaDB (Base vectorielle)
           ↓
    🔍 Retriever (Recherche sémantique)
           ↓
    📝 Context + Prompt + Query Rewriting
           ↓
    🦙 Ollama Phi3 (LLM local)
           ↓
    ✨ Réponse finale
```

### Détails du processus

1. **Documents** : Fichier `data.txt` contenant toutes les informations sur Asma
2. **Chunking** : Découpage du texte en morceaux de 500 caractères avec chevauchement
3. **Embeddings** : Conversion des chunks en vecteurs numériques multilingues
4. **ChromaDB** : Stockage des vecteurs pour recherche rapide
5. **Query Rewriting** : Reformulation intelligente de la question avec historique
6. **Retriever** : Récupération des 3 chunks les plus pertinents
7. **Context + Prompt** : Construction du prompt avec contexte formaté
8. **Ollama Phi3** : Génération de la réponse par le LLM local
9. **Réponse finale** : Affichage dans l'interface utilisateur

## Fonctionnalités

- **RAG (Retrieval-Augmented Generation)** : Récupération intelligente d'informations
- **Interface élégante et féminine** : Design moderne avec animations fluides
- **Conversations naturelles** : Propulsé par Ollama Phi3 (100% local et gratuit)
- **Query Rewriting** : Reformulation intelligente des questions avec historique
- **Base de connaissances vectorielle** : ChromaDB pour recherche sémantique
- **Historique de conversation** : Contexte maintenu pour cohérence
- **API REST** : Backend FastAPI performant
- **Responsive** : Fonctionne sur desktop et mobile
- **Aucun coût d'API** : Tout fonctionne en local

## Technologies utilisées

### Backend
- **FastAPI** : Framework web moderne et rapide
- **Ollama Phi3** : LLM local (2.2 GB, gratuit)
- **LangChain** : Framework pour applications LLM
- **ChromaDB** : Base de données vectorielle
- **Sentence Transformers** : Génération d'embeddings multilingues

### Frontend
- **HTML5/CSS3** : Interface moderne avec animations CSS
- **JavaScript Vanilla** : Pas de framework, performances optimales
- **Google Fonts** : Typographie élégante (Poppins, Playfair Display)

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Ollama installé (https://ollama.ai)
- Modèle Phi3 téléchargé (`ollama pull phi3`)

## Installation

### 1. Installer Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Téléchargez depuis https://ollama.ai/download

### 2. Télécharger le modèle Phi3

```bash
ollama pull phi3
```

### 3. Cloner le projet

```bash
git clone https://github.com/asma-tk/asma-rag-chatbot.git
cd asma-rag-chatbot
```

### 4. Créer un environnement virtuel

```bash
python3 -m venv venv
```

### 5. Activer l'environnement virtuel

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 6. Installer les dépendances

```bash
pip install -r requirements.txt
```

L'installation peut prendre quelques minutes (téléchargement des modèles d'embeddings).

### 7. Personnaliser les données

Éditez le fichier `data.txt` avec vos propres informations personnelles. Le fichier actuel contient les informations d'Asma Taberkokt comme exemple.

## Utilisation

### Méthode 1 : Script de démarrage (Recommandé)

```bash
./start.sh
```

Le script vérifie automatiquement :
- Environnement virtuel
- Ollama en cours d'exécution
- Modèle phi3 installé

### Méthode 2 : Démarrage manuel

```bash
# Démarrer Ollama (si pas déjà démarré)
ollama serve

# Dans un autre terminal
source venv/bin/activate
python3 app.py
```

Le serveur démarrera sur `http://localhost:8000`

Vous verrez dans les logs :
```
🚀 Démarrage de l'application...
✓ Modèle d'embeddings initialisé
✓ ChromaDB initialisé
✓ Ollama phi3 connecté et fonctionnel
✓ Fichier chargé (XXX caractères)
✓ Texte découpé en XX chunks
✓ XX chunks indexés dans ChromaDB
✅ Application prête!
```

### Accéder au chatbot

Ouvrez votre navigateur et allez sur :
```
http://localhost:8000
```

### Exemples de questions

Essayez de poser ces questions au chatbot :

- "Parle-moi de ton parcours"
- "Quelles sont tes compétences en IA ?"
- "Quels sont tes objectifs professionnels ?"
- "Quelles langues parles-tu ?"
- "Quels sont tes hobbies ?"
- "Pourquoi as-tu choisi l'IA ?"
- "Où te vois-tu dans 3 ans ?"
- "Quels sont tes projets ?"

### Commandes spéciales

Dans l'interface du chatbot, vous pouvez utiliser :

- `/clear` : Effacer l'historique de conversation
- `/stats` : Afficher les statistiques du système

## 📁 Structure du projet

```
chatbot/
│
├── app.py                    # Backend FastAPI avec logique RAG
├── data.txt                  # Base de connaissances (à personnaliser)
├── index.html                # Interface utilisateur
├── style.css                 # Styles élégants et féminins
├── script.js                 # Logique frontend
├── requirements.txt          # Dépendances Python
├── .env.example              # Template de configuration
├── .env                      # Configuration (à créer)
├── README.md                 # Ce fichier
│
├── venv/                     # Environnement virtuel Python
├── chroma_db/                # Base de données ChromaDB (créé auto)
│
└── .gitignore                # Fichiers à ignorer par Git
```

## 🔧 Configuration avancée

### Modifier le modèle Claude

Dans `app.py`, ligne 155 :

```python
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",  # Changez le modèle ici
    anthropic_api_key=ANTHROPIC_API_KEY,
    temperature=0.7,  # Ajustez la créativité (0-1)
    max_tokens=1024   # Longueur maximale de réponse
)
```

Modèles disponibles :
- `claude-3-5-sonnet-20241022` (recommandé - équilibre performance/coût)
- `claude-3-opus-20240229` (plus puissant mais plus cher)
- `claude-3-sonnet-20240229` (bon équilibre)
- `claude-3-haiku-20240307` (plus rapide et économique)

### Modifier les paramètres de chunking

Dans `app.py`, ligne 107 :

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Taille des chunks (caractères)
    chunk_overlap=50,    # Chevauchement entre chunks
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

**Recommandations :**
- `chunk_size` : 300-800 caractères (500 par défaut)
- `chunk_overlap` : 10-20% de chunk_size (50 par défaut)

### Modifier le nombre de contextes récupérés

Dans `app.py`, ligne 268 :

```python
context = retrieve_relevant_context(request.message, k=3)  # k = nombre de chunks
```

**Recommandations :**
- `k=1-2` : Réponses plus précises mais moins de contexte
- `k=3-5` : Bon équilibre (3 par défaut)
- `k=5+` : Plus de contexte mais risque de bruit

## 🎨 Personnalisation de l'interface

### Modifier les couleurs

Dans `style.css`, lignes 8-18 :

```css
:root {
    --primary-color: #E8B4F0;      /* Rose-violet principal */
    --primary-dark: #D896E8;       /* Rose-violet foncé */
    --secondary-color: #B8E8F0;    /* Bleu clair */
    --accent-color: #FFB6D9;       /* Rose accent */
    --bg-gradient-1: #FFF5F7;      /* Fond gradient 1 */
    --bg-gradient-2: #F0E8FF;      /* Fond gradient 2 */
}
```

### Modifier les polices

Dans `index.html`, ligne 10 :

```html
<link href="https://fonts.googleapis.com/css2?family=VotrePolice&display=swap" rel="stylesheet">
```

Puis dans `style.css` :

```css
body {
    font-family: 'VotrePolice', sans-serif;
}
```

## 🐛 Dépannage

### Erreur : "ANTHROPIC_API_KEY non définie"

**Solution :** Vérifiez que le fichier `.env` existe et contient votre clé API.

```bash
# Vérifier le contenu du .env
cat .env
```

### Erreur : "Impossible de résoudre l'importation"

**Solution :** Assurez-vous que l'environnement virtuel est activé et que les dépendances sont installées :

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Le serveur ne démarre pas

**Solution :** Vérifiez que le port 8000 n'est pas déjà utilisé :

```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

Pour utiliser un autre port :

```bash
uvicorn app:app --port 8080
```

### Erreur CORS dans le navigateur

**Solution :** Le CORS est déjà configuré dans `app.py`. Assurez-vous d'accéder au chatbot via `http://localhost:8000` et non en ouvrant directement le fichier HTML.

### ChromaDB ne s'initialise pas

**Solution :** Supprimez le dossier `chroma_db` et relancez le serveur :

```bash
rm -rf chroma_db
python app.py
```

### Erreur de mémoire lors du chargement des embeddings

**Solution :** Le modèle d'embeddings est chargé en CPU par défaut. Si vous avez peu de RAM, utilisez un modèle plus léger dans `app.py` :

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Plus léger
)
```

## 📊 API Endpoints

### POST /chat
Envoyer un message au chatbot

**Request:**
```json
{
  "message": "Quelles sont tes compétences ?",
  "conversation_history": [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
  ]
}
```

**Response:**
```json
{
  "response": "Mes compétences principales sont...",
  "sources": ["contexte 1", "contexte 2"]
}
```

### GET /health
Vérifier l'état du serveur

**Response:**
```json
{
  "status": "healthy",
  "chroma_documents": 42
}
```

### GET /stats
Obtenir les statistiques du système

**Response:**
```json
{
  "total_documents": 42,
  "model": "claude-3-5-sonnet-20241022",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

## 🚀 Déploiement

### Déploiement local avec Uvicorn

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Déploiement en production

```bash
# Sans reload pour la production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Déploiement sur le cloud

**Render, Railway, Fly.io :**

1. Créez un `Procfile` :
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

2. Configurez les variables d'environnement dans le dashboard

3. Déployez depuis GitHub

**Docker :**

Créez un `Dockerfile` :
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construisez et lancez :
```bash
docker build -t chatbot-rag .
docker run -p 8000:8000 --env-file .env chatbot-rag
```

## 🔒 Sécurité

- ⚠️ **Ne commitez JAMAIS** votre fichier `.env` avec votre clé API
- ⚠️ Ajoutez `.env` à votre `.gitignore`
- ⚠️ Utilisez des variables d'environnement en production
- ⚠️ Limitez l'accès à votre API avec des tokens si nécessaire
- ⚠️ Activez HTTPS en production
- ⚠️ Implémentez un rate limiting pour éviter les abus

## 💰 Coûts estimés

**Claude API (Anthropic) :**
- Claude 3.5 Sonnet : ~$3 par million de tokens input, ~$15 par million de tokens output
- Estimation : ~$0.01-0.05 par conversation de 10 messages

**Hébergement :**
- Gratuit : Render, Railway (tier gratuit)
- Payant : À partir de $5-10/mois

## 📈 Améliorations futures

- [ ] Authentification utilisateur
- [ ] Support multilingue automatique
- [ ] Export des conversations en PDF
- [ ] Mode vocal (speech-to-text)
- [ ] Intégration avec d'autres LLMs (GPT-4, Gemini)
- [ ] Dashboard d'administration
- [ ] Analytics et métriques
- [ ] Cache des réponses fréquentes
- [ ] Support des images et fichiers
- [ ] Mode hors ligne avec modèles locaux
- [ ] Fine-tuning du modèle
- [ ] A/B testing des prompts

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est libre d'utilisation pour des projets personnels et éducatifs.

## 👩‍💻 Auteur

**Asma Taberkokt**
- 🎓 Développeuse IA en formation
- 🤖 Passionnée par la robotique et les systèmes agentiques
- 🌟 Rêve de créer une entreprise IA reconnue mondialement
- 🌍 Polyglotte (6 langues courantes)
- 🎯 Objectif : Silicon Valley et impact positif sur la société

## 🙏 Remerciements

- **Anthropic** pour Claude AI
- **LangChain** pour le framework RAG
- **ChromaDB** pour la base vectorielle
- **Sentence Transformers** pour les embeddings multilingues
- **FastAPI** pour le framework web
- La communauté open source

## 📚 Ressources utiles

- [Documentation LangChain](https://python.langchain.com/)
- [Documentation Anthropic](https://docs.anthropic.com/)
- [Documentation ChromaDB](https://docs.trychroma.com/)
- [Guide RAG](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

Créé avec ❤️ et ✨ par Asma Taberkokt

**Besoin d'aide ?** Ouvrez une issue sur GitHub ou contactez-moi !

🚀 **Prêt à démarrer ?** Suivez les instructions d'installation ci-dessus !