"""
Chatbot RAG avec FastAPI, ChromaDB et Groq
Chatbot personnel pour Asma Taberkokt
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
from dotenv import load_dotenv
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger
from groq import Groq

# Charger les variables d'environnement
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
DATA_FILE = "data.txt"

# Client Groq
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
logger.info(f"Groq configuré avec le modèle {GROQ_MODEL}")

# Initialiser FastAPI
app = FastAPI(
    title="Chatbot Personnel Asma",
    description="Chatbot RAG avec Groq pour répondre aux questions sur Asma Taberkokt",
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

# Statut d'initialisation : permet à /health de répondre immédiatement
# pendant que le chargement du modèle + l'indexation se font en tâche de fond
init_status = {"ready": False, "error": None}

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
    
    logger.info("Indexation des données dans ChromaDB (par lot)...")

    # embed_documents() encode tous les chunks en un seul appel batché,
    # au lieu de 87 appels embed_query() séquentiels — bien plus rapide
    # et beaucoup moins gourmand en CPU au démarrage.
    batch_embeddings = embeddings.embed_documents(chunks)
    ids = [f"doc_{i}" for i in range(len(chunks))]

    collection.add(
        embeddings=batch_embeddings,
        documents=chunks,
        ids=ids
    )

    logger.info(f"✓ {len(chunks)} chunks indexés dans ChromaDB (en 1 lot)")



def groq_chat(messages: List[dict], temperature: float = 0.3, max_tokens: int = 500) -> str:
    """Appelle l'API chat de Groq."""
    if not groq_client:
        raise RuntimeError("GROQ_API_KEY non configurée. Ajoutez la variable d'environnement GROQ_API_KEY.")
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content.strip()

def rewrite_query(question: str, history: List[dict]) -> str:
    """
    Reformule la question utilisateur pour améliorer la recherche RAG.
    """
    if not history or len(history) == 0:
        return question

    history_parts = []
    for i in range(0, len(history[-6:]), 2):
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
        rewritten = groq_chat([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ], temperature=0.2, max_tokens=100)
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
    """Génère une réponse avec Groq en utilisant le contexte RAG"""
    if not context:
        context_text = "Aucune information trouvée dans la base."
    else:
        context_parts = []
        for i, chunk in enumerate(context, 1):
            context_parts.append(f"[Extrait {i}]\n{chunk}")
        context_text = "\n\n---\n\n".join(context_parts)

    system_prompt = f"""Tu es un assistant virtuel spécialisé dans le profil d'Asma Taberkokt, développeuse en Intelligence Artificielle en formation certifiante Microsoft by Simplon.

IMPORTANT : Tu parles D'Asma à la troisième personne (elle, son, sa, ses). Tu n'es PAS Asma.

Ta mission :
Aider les visiteurs à découvrir Asma, son parcours, ses compétences, ses projets et sa recherche de stage.

---

INFORMATIONS CLÉS À CONNAÎTRE ABSOLUMENT :

Stage recherché :
- Asma recherche un stage en machine learning du 22 juin 2026 au 19 novembre 2026 (700 heures, 100 jours, 35h/semaine).
- La convention est une PAE (Période d'Application en Entreprise), convention tripartite entre Simplon, l'entreprise d'accueil et Asma.
- Un regroupement obligatoire au centre de formation Simplon est prévu le 10 septembre 2026.
- Elle est disponible pour des opportunités de stage, des collaborations IA, et des échanges professionnels.
- Elle répond généralement sous 24 à 48 heures.

Gratification du stage :
- Le stage relève de la formation professionnelle continue, pas du Code de l'éducation.
- Aucune gratification minimale n'est légalement obligatoire, quelle que soit la durée du stage.
- L'entreprise d'accueil peut choisir de verser une gratification à titre facultatif.
- Asma bénéficie néanmoins des protections des salariés (non-discrimination, harcèlement, etc.) selon le Code du travail.

Contacts Simplon pour le stage :
- Chef de projet formation : Nicolas PIQUET — npiquet@simplon.co / 06 72 18 49 98
- Formateur référent : Maxime MULLER — mmuller@simplon.co
- Lieu de formation : La Cité, 55 avenue Louis Bréguet, 31400 Toulouse

Formation Microsoft by Simplon :
- Asma suit depuis décembre 2025 une formation certifiante "Développeur en Intelligence Artificielle" chez Microsoft by Simplon.
- La certification professionnelle est prévue pour décembre 2026.
- Volume horaire total : 917h en formation + 700h en entreprise.
- La formation couvre : conception et entraînement de modèles ML, manipulation de bases de données, intégration d'outils LLM, développement de systèmes RAG, utilisation de vector embeddings.
- Elle a aussi suivi en 2025 le programme Apple Foundation Program chez Simplon (développement iOS, Swift, UX design).
- Le référentiel couvre 3 blocs : collecte et stockage de données (C1-C5), intégration de modèles IA (C6-C13), réalisation d'applications IA (C14-C21).

Parcours avant Simplon :
- Master en Génie des Procédés, Université Saad Dahleb (2019).
- Stage chez SNC LAVALIN sur le contrôle qualité de membranes d'osmose inverse.
- Sa reconversion vers l'IA est motivée par une passion profonde pour l'innovation et l'impact positif sur la société.

Langues maîtrisées par Asma :
- Kabyle (langue maternelle) - Niveau natif
- Arabe - Niveau courant
- Français - Niveau courant
- Anglais - IELTS Academic B2 / C2 CECRL
- Allemand - CECRL B2
- Turc - Niveau courant
- Espagnol - Niveau débutant (en apprentissage)
- Chinois - Niveau débutant (en apprentissage)

Contact Asma :
- Email : asmataberkokt@gmail.com
- Téléphone : 06 02 95 42 58
- LinkedIn : linkedin.com/in/asma-t-5b71b6217
- GitHub : https://github.com/asma-tk

---

Ton expertise :
- Tu connais parfaitement ses compétences en RAG, Computer Vision, Agentique, IA Générative, MLOps, NLP, Deep Learning.
- Tu comprends son parcours Simplon, les conditions de son stage et sa gratification.
- Tu peux expliquer le contenu de sa formation et les compétences du référentiel de certification.
- Tu connais toutes les langues qu'elle parle et leur niveau de maîtrise.

Ton style :
- Tu es enjouée, énergique, accueillante et naturelle.
- Tu as une petite personnalité chaleureuse et motivante.
- Tu restes professionnelle, mais pas froide ni robotique.
- Tu parles toujours à la troisième personne quand tu parles d'Asma.

Règles de réponse :
- Réponds principalement à partir du contexte fourni ci-dessous, complété par les infos clés ci-dessus.
- Pour les questions sur le stage : donne systématiquement les dates exactes, la durée, le domaine, et les coordonnées de contact.
- Pour les questions sur la gratification : explique clairement que la loi n'impose aucune gratification (formation pro continue), mais que l'entreprise peut en verser une volontairement.
- Pour les questions sur Simplon ou la formation : explique le contenu, la durée, la certification Microsoft, et les blocs de compétences si pertinent.
- Pour les compétences : cherche dans les sections "COMPÉTENCES PROFESSIONNELLES PRINCIPALES" et "COMPÉTENCES TECHNIQUES IA & LLM".
- Pour les langues : donne la liste complète avec les niveaux (Kabyle natif, Arabe courant, Français courant, Anglais B2/C2, Allemand B2, Turc courant, Espagnol et Chinois débutant).
- Si une question utilise des mots différents (ex : hobbies, loisirs, passions, centres d'intérêt, langues parlées, compétences linguistiques), comprends qu'il s'agit du même type d'information.
- Si plusieurs informations partielles sont présentes, regroupe-les pour construire une réponse cohérente.
- Ne fabrique jamais d'informations absentes du contexte ou des infos clés ci-dessus.
- Si l'information est vraiment absente, dis : "Désolée, je ne peux pas t'aider avec ça pour le moment, mais je t'invite à prendre contact avec Asma directement sur LinkedIn : linkedin.com/in/asma-t-5b71b6217"
- Exception projets : si tu n'as pas assez d'infos, donne les éléments disponibles puis ajoute : "Pour en voir plus, tu peux aussi consulter son GitHub : https://github.com/asma-tk ou son LinkedIn : linkedin.com/in/asma-t-5b71b6217"
- Mets en forme ta réponse pour qu'elle soit facile à lire, pas un bloc de texte.
- Ne dépasse pas environ 10 à 15 phrases sauf si l'utilisateur demande une réponse plus longue.
- Quand c'est pertinent, termine par une ouverture naturelle comme : "Tu veux en savoir plus sur ce sujet ?" ou "Je peux aussi te donner plus de détails si tu veux."
- N'utilise jamais de markdown : pas de **, pas de __, pas de listes markdown, pas de crochets autour des liens.
- Quand tu donnes un lien, écris-le une seule fois, proprement.

Si la question porte sur les projets :
- Donne une vue globale.
- Ne te limite pas à un seul projet.
- Mentionne plusieurs types de projets si possible.

Tu dois donner envie d'en apprendre plus sur Asma, tout en restant concise et honnête.

Contexte sur Asma Taberkokt :
{context_text}"""

    user_prompt = f"Question : {query}"
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    try:
        content = groq_chat(messages, temperature=0.3, max_tokens=500)
        content = content.replace("**", "").replace("__", "")
        content = content.replace("•", "-")
        return content.strip()
    except Exception as e:
        logger.error(f"Erreur lors de la génération de réponse: {e}")
        return f"Désolé, je rencontre un problème technique avec Groq. Erreur: {str(e)}"


def _run_heavy_initialization():
    """Contient tout le travail bloquant (modèle, ChromaDB, indexation).
    Exécuté hors de la boucle asyncio via un threadpool, pour ne jamais
    bloquer le démarrage du serveur ni le healthcheck."""
    global init_status
    try:
        initialize_embeddings()
        initialize_chromadb()

        chunks = load_and_process_data()
        index_data(chunks)

        init_status["ready"] = True
        logger.info("✅ Application prête!")

    except Exception as e:
        init_status["error"] = str(e)
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")


@app.on_event("startup")
async def startup_event():
    """Démarrage de l'application : ne fait qu'un check rapide puis
    lance l'initialisation lourde en arrière-plan, sans bloquer.
    Le serveur (et /health) répond donc immédiatement."""
    logger.info("🚀 Démarrage de l'application...")

    if not GROQ_API_KEY:
        logger.warning("⚠️ GROQ_API_KEY non définie. Le chatbot ne fonctionnera pas sans cette clé.")
    else:
        logger.info("✓ GROQ_API_KEY configurée")

    # Lance l'initialisation lourde (modèle + ChromaDB + indexation) dans
    # un thread séparé, sans attendre qu'elle finisse pour terminer le
    # démarrage. Le serveur commence donc à répondre tout de suite.
    asyncio.create_task(run_in_threadpool(_run_heavy_initialization))

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Chatbot API Asma Taberkokt",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "stats": "/stats"
        },
        "groq": {
            "model": GROQ_MODEL,
            "api_key_set": bool(GROQ_API_KEY),
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de santé : répond toujours 200 dès que le serveur écoute,
    même si l'indexation ChromaDB tourne encore en arrière-plan."""
    return {
        "status": "healthy" if init_status["ready"] else "initializing",
        "init_error": init_status["error"],
        "chroma_documents": collection.count() if collection else 0,
        "model": GROQ_MODEL,
        "groq_api_key_set": bool(GROQ_API_KEY),
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal pour le chat"""
    try:
        logger.info(f"Question reçue: {request.message}")
        
        if not GROQ_API_KEY:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY non configurée. Ajoutez la variable d'environnement dans Railway.")

        if not init_status["ready"]:
            raise HTTPException(status_code=503, detail="Le chatbot est encore en cours d'initialisation, réessayez dans quelques secondes.")

        rewritten_query = rewrite_query(
            request.message,
            request.conversation_history or []
        )
        
        search_query = rewritten_query if rewritten_query != request.message else request.message
        
        context = retrieve_relevant_context(search_query, k=3)
        logger.info(f"Contexte récupéré: {len(context)} chunks")
        
        response = generate_response(
            request.message,
            context,
            request.conversation_history or []
        )
        
        logger.info(f"Réponse générée: {response[:100]}...")
        
        return ChatResponse(
            response=response,
            sources=context[:2]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Statistiques du système"""
    return {
        "total_documents": collection.count() if collection else 0,
        "model": GROQ_MODEL,
        "embedding_model": "all-MiniLM-L6-v2",
        "groq_api_key_set": bool(GROQ_API_KEY),
    }