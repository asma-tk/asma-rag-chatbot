# 🤖 Chatbot RAG - Asma Taberkokt

Chatbot intelligent utilisant RAG (Retrieval-Augmented Generation) avec FastAPI, ChromaDB et Groq API.

## 📁 Structure du Projet

```
chatbot/
├── frontend/          # Frontend statique (Netlify)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── robot.png
│   └── netlify.toml
│
├── backend/           # Backend Python (Render)
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   ├── data.txt
│   └── RENDER_DEPLOYMENT.md
│
└── README.md
```

## 🚀 Déploiement

### Frontend (Netlify)
1. Connectez le dossier `frontend/` à Netlify
2. Netlify détectera automatiquement `netlify.toml`
3. Le site sera déployé en ~30 secondes

### Backend (Render)
1. Connectez le dossier `backend/` à Render
2. Render utilisera `render.yaml` et `Dockerfile`
3. Le backend sera déployé en ~10-15 minutes

## 🔗 URLs

- **Frontend** : https://votre-site.netlify.app
- **Backend** : https://asma-rag-chatbot-2.onrender.com

## 📚 Documentation

- Frontend : Voir `frontend/netlify.toml`
- Backend : Voir `backend/RENDER_DEPLOYMENT.md`

## 🛠️ Technologies

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : FastAPI, ChromaDB, Groq API, Docker
- **Hosting** : Netlify (frontend) + Render (backend)