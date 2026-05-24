"""
Chatbot RAG avec FastAPI, ChromaDB et Groq API
Chatbot personnel pour Asma Taberkokt
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from loguru import logger

# Patch de compatibilité httpx/groq
import httpx
_original_init = httpx.Client.__init__
def _patched_init(self, *args, **kwargs):
    kwargs.pop("proxies", None)
    _original_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_init

from groq import Groq

# Charger les variables d'environnement
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY non définie dans le fichier .env")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
DATA_FILE = "data.txt"

# Initialiser le client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialiser FastAPI
app = FastAPI(
    title="Chatbot Personnel Asma",
    description="Chatbot RAG avec Ollama Phi3 pour répondre aux questions sur Asma Taberkokt",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []

# Variables globales
chroma_client = None
collection = None
embeddings = None

def initialize_embeddings():
    """Initialise le modèle d'embeddings"""
    global embeddings
    logger.info("Initialisation du modèle d'embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    logger.info("✓ Modèle d'embeddings initialisé")

def initialize_chromadb():
    """Initialise ChromaDB"""
    global chroma_client, collection
    logger.info("Initialisation de ChromaDB...")
    
    os.makedirs(CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
    
    try:
        collection = chroma_client.get_collection(name="asma_knowledge")
        logger.info("✓ Collection existante récupérée")
    except:
        collection = chroma_client.create_collection(
            name="asma_knowledge",
            metadata={"description": "Connaissances sur Asma Taberkokt"}
        )
        logger.info("✓ Nouvelle collection créée")

def load_and_process_data():
    """Charge et traite les données du fichier texte"""
    logger.info(f"Chargement des données depuis {DATA_FILE}...")
    
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Le fichier {DATA_FILE} n'existe pas")
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    logger.info(f"✓ Fichier chargé ({len(text)} caractères)")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    logger.info(f"✓ Texte découpé en {len(chunks)} chunks")
    
    return chunks

def index_data(chunks: List[str]):
    """Indexe les données dans ChromaDB"""
    global collection, embeddings
    
    if collection.count() > 0:
        logger.info(f"✓ Collection déjà indexée ({collection.count()} documents)")
        return
    
    logger.info("Indexation des données dans ChromaDB...")
    
    for i, chunk in enumerate(chunks):
        embedding = embeddings.embed_query(chunk)
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            ids=[f"doc_{i}"]
        )
    
    logger.info(f"✓ {len(chunks)} chunks indexés dans ChromaDB")

def test_groq_connection():
    """Teste la connexion à Groq API"""
    logger.info(f"Test de connexion à Groq avec le modèle {GROQ_MODEL}...")
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{'role': 'user', 'content': 'Bonjour'}],
            max_tokens=10
        )
        logger.info(f"✓ Groq {GROQ_MODEL} connecté et fonctionnel")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à Groq: {e}")
        logger.error(f"Vérifiez votre clé API GROQ_API_KEY dans le fichier .env")
        return False

def rewrite_query(question: str, history: List[dict]) -> str:
    """
    Reformule la question utilisateur pour améliorer la recherche RAG.
    Inspiré de MimiBot - adapté pour Groq.
    """
    if not history or len(history) == 0:
        # Pas d'historique, on retourne la question telle quelle
        return question
    
    # Construire l'historique des 3 dernières interactions
    # Format: {role: 'user'/'assistant', content: 'message'}
    history_parts = []
    for i in range(0, len(history[-6:]), 2):  # Prendre les 3 dernières paires
        if i + 1 < len(history[-6:]):
            user_msg = history[-6:][i]
            assistant_msg = history[-6:][i + 1]
            
            if user_msg.get('role') == 'user' and assistant_msg.get('role') == 'assistant':
                part = f"Utilisateur : {user_msg.get('content', '')}\nAsma : {assistant_msg.get('content', '')}"
                history_parts.append(part)
    
    history_text = "\n\n".join(history_parts) if history_parts else "Aucun historique."
    
    system_prompt = """Tu es un assistant qui reformule des questions pour améliorer une recherche documentaire.

Règles :
- Tu ne réponds JAMAIS à la question
- Tu reformules seulement pour rendre la question plus claire
- Tu peux expliciter l'intention
- Tu peux ajouter des synonymes utiles
- Si l'historique aide à comprendre, utilise-le
- Retourne UNE SEULE reformulation, sans explication"""

    user_prompt = f"""Historique :
{history_text}

Question actuelle :
{question}

Reformule cette question pour optimiser une recherche sur Asma Taberkokt, son profil, ses projets, ses compétences et ses centres d'intérêt."""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=0.2,
            max_tokens=100
        )
        rewritten = response.choices[0].message.content.strip()
        logger.info(f"Question reformulée: {question} → {rewritten}")
        return rewritten
    except Exception as e:
        logger.warning(f"Erreur reformulation: {e}, utilisation question originale")
        return question

def retrieve_relevant_context(query: str, k: int = 3) -> List[str]:
    """Récupère les contextes pertinents depuis ChromaDB"""
    global collection, embeddings
    
    query_embedding = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    
    return results['documents'][0] if results['documents'] else []

def generate_response(query: str, context: List[str], conversation_history: List[dict]) -> str:
    """Génère une réponse avec Ollama Phi3 en utilisant le contexte RAG"""
    
    # Formatage du contexte
    if not context:
        context_text = "Aucune information trouvée dans la base."
    else:
        context_parts = []
        for i, chunk in enumerate(context, 1):
            context_parts.append(f"[Extrait {i}]\n{chunk}")
        context_text = "\n\n---\n\n".join(context_parts)

    # Prompt : assistant qui donne des informations SUR Asma (3ème personne)
    system_prompt = f"""Tu es un assistant virtuel qui aide les visiteurs à découvrir le profil d'Asma Taberkokt.

IMPORTANT : Tu parles D'Asma à la troisième personne (elle, son, sa, ses). Tu n'es PAS Asma.

Ton style :
- Tu es professionnel, clair et direct
- Tu restes naturel et accessible
- Tu réponds de façon simple et précise
- Tu parles toujours à la troisième personne quand tu parles d'Asma

Règles de réponse :
- Réponds UNIQUEMENT à partir des informations ci-dessous sur Asma
- Reformule et synthétise les informations présentes
- Si plusieurs informations partielles sont présentes, regroupe-les
- Ne fabrique JAMAIS d'informations qui ne sont pas dans le contexte
- Si la question utilise des mots différents (ex : études, formation, diplômes), comprends qu'il s'agit du même type d'information
- Si l'information n'est pas disponible, dis : "Je n'ai pas cette information pour le moment."
- Évite les réponses trop longues (maximum 10-15 phrases)
- N'utilise PAS de markdown (pas de **, pas de __, pas de listes)
- Quand tu donnes un lien ou email, écris-le proprement

Informations sur Asma Taberkokt :
{context_text}"""

    user_prompt = f"Question : {query}"

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            top_p=0.9,
            max_tokens=500
        )
        
        # Nettoyage du markdown comme dans MimiBot
        content = response.choices[0].message.content
        content = content.replace("**", "").replace("__", "")
        content = content.replace("•", "-")
        
        return content.strip()
    except Exception as e:
        logger.error(f"Erreur lors de la génération de réponse: {e}")
        return f"Désolé, je rencontre un problème technique avec l'API Groq. Erreur: {str(e)}"

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    try:
        logger.info("🚀 Démarrage de l'application...")
        
        initialize_embeddings()
        initialize_chromadb()
        
        if not test_groq_connection():
            logger.warning("⚠️ Ollama n'est pas disponible. Le chatbot ne fonctionnera pas correctement.")
        
        chunks = load_and_process_data()
        index_data(chunks)
        
        logger.info("✅ Application prête!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

@app.get("/")
async def root():
    """Sert la page HTML principale"""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "chroma_documents": collection.count() if collection else 0,
        "model": GROQ_MODEL
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal pour le chat"""
    try:
        logger.info(f"Question reçue: {request.message}")
        
        # Reformulation de la requête si historique disponible
        rewritten_query = rewrite_query(
            request.message,
            request.conversation_history or []
        )
        
        # Utiliser la requête reformulée pour la recherche
        search_query = rewritten_query if rewritten_query != request.message else request.message
        
        context = retrieve_relevant_context(search_query, k=3)
        logger.info(f"Contexte récupéré: {len(context)} chunks")
        
        # Générer la réponse avec la question ORIGINALE (pas reformulée)
        response = generate_response(
            request.message,  # Question originale pour la réponse
            context,
            request.conversation_history or []
        )
        
        logger.info(f"Réponse générée: {response[:100]}...")
        
        return ChatResponse(
            response=response,
            sources=context[:2]
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Statistiques du système"""
    return {
        "total_documents": collection.count() if collection else 0,
        "model": GROQ_MODEL,
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
    }

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    # Utiliser le port fourni par Render (variable d'environnement PORT)
    # ou 8000 par défaut pour le développement local
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )