# 🚀 Guide de Déploiement sur Netlify

## 📋 Prérequis

- ✅ Backend déployé sur Render : https://asma-rag-chatbot-2.onrender.com
- ✅ Code frontend prêt avec `script.js` pointant vers l'API Render
- ✅ Compte Netlify (gratuit)

---

## 🎯 Étapes de Déploiement

### **Étape 1 : Préparer le Repository**

Les fichiers suivants sont nécessaires pour Netlify :
- ✅ `index.html` - Page principale
- ✅ `style.css` - Styles
- ✅ `script.js` - Logique frontend (API_URL configuré)
- ✅ `robot.png` - Avatar du bot
- ✅ `netlify.toml` - Configuration Netlify

### **Étape 2 : Pousser les Changements sur GitHub**

```bash
cd /Users/asmataberkokt/chatbot
git add script.js netlify.toml NETLIFY_DEPLOYMENT.md
git commit -m "Prepare frontend for Netlify deployment"
git push origin main
```

### **Étape 3 : Créer un Nouveau Site sur Netlify**

1. **Allez sur** : https://app.netlify.com
2. **Connectez-vous** avec votre compte
3. **Cliquez sur** : "Add new site" → "Import an existing project"
4. **Sélectionnez** : "Deploy with GitHub"
5. **Autorisez** Netlify à accéder à vos repositories
6. **Cherchez et sélectionnez** : `asma-tk/asma-rag-chatbot`

### **Étape 4 : Configuration du Build**

Netlify détectera automatiquement `netlify.toml`, mais vérifiez :

- **Branch to deploy** : `main`
- **Build command** : (laissez vide ou `echo 'Static site'`)
- **Publish directory** : `.` (racine du projet)

### **Étape 5 : Déployer**

1. **Cliquez sur** : "Deploy site"
2. **Attendez** ~1-2 minutes (très rapide pour un site statique)
3. **Votre site sera accessible** à : `https://random-name-123.netlify.app`

### **Étape 6 : Personnaliser le Nom de Domaine (Optionnel)**

1. **Allez dans** : Site settings → Domain management
2. **Cliquez sur** : "Options" → "Edit site name"
3. **Changez en** : `asma-chatbot` ou votre choix
4. **Nouvelle URL** : `https://asma-chatbot.netlify.app`

---

## 🔧 Configuration Technique

### Fichier `netlify.toml`

```toml
[build]
  publish = "."
  command = "echo 'No build command needed for static site'"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### API URL dans `script.js`

```javascript
const API_URL = 'https://asma-rag-chatbot-2.onrender.com';
```

---

## 📊 Architecture Finale

```
┌─────────────────────────────────────────────┐
│              ARCHITECTURE                    │
├─────────────────────────────────────────────┤
│                                              │
│  Frontend (Netlify)                          │
│  ├─ index.html                               │
│  ├─ style.css                                │
│  ├─ script.js                                │
│  └─ robot.png                                │
│           │                                  │
│           │ HTTPS Requests                   │
│           ↓                                  │
│  Backend (Render)                            │
│  ├─ FastAPI                                  │
│  ├─ ChromaDB                                 │
│  ├─ Groq API                                 │
│  └─ Embeddings                               │
│                                              │
└─────────────────────────────────────────────┘
```

---

## ✅ Vérifications Post-Déploiement

### 1. **Tester le Frontend**
```
https://votre-site.netlify.app
```

### 2. **Vérifier la Console du Navigateur**
- Ouvrir DevTools (F12)
- Onglet Console
- Vérifier qu'il n'y a pas d'erreurs CORS

### 3. **Tester une Question**
- Poser une question dans le chatbot
- Vérifier que la réponse arrive du backend Render

---

## 🔍 Résolution de Problèmes

### **Problème : Erreur CORS**

**Symptôme** :
```
Access to fetch at 'https://asma-rag-chatbot-2.onrender.com/chat' 
from origin 'https://votre-site.netlify.app' has been blocked by CORS policy
```

**Solution** : Le backend Render a déjà CORS configuré avec `allow_origins=["*"]`, donc ça devrait fonctionner. Si problème, vérifiez que l'API Render est bien en ligne.

### **Problème : API ne répond pas**

**Causes possibles** :
1. Backend Render en veille (plan gratuit)
2. URL API incorrecte dans `script.js`

**Solution** :
1. Ouvrir `https://asma-rag-chatbot-2.onrender.com/health` pour réveiller le backend
2. Vérifier l'URL dans `script.js`

### **Problème : Image robot.png ne s'affiche pas**

**Solution** : Vérifier que `robot.png` est bien dans le repository et poussé sur GitHub.

---

## 🚀 Déploiements Automatiques

Netlify redéploiera automatiquement à chaque push sur `main` :

```bash
# Modifier vos fichiers frontend
git add index.html style.css script.js
git commit -m "Update frontend"
git push origin main
# Netlify redéploie automatiquement en ~30 secondes
```

---

## 📊 Avantages de Netlify

- ✅ **Gratuit** pour sites statiques
- ✅ **CDN global** (chargement ultra-rapide)
- ✅ **HTTPS automatique**
- ✅ **Déploiements automatiques** depuis GitHub
- ✅ **Prévisualisations** des Pull Requests
- ✅ **Rollback facile** vers versions précédentes

---

## 🎯 URLs Finales

Après déploiement, vous aurez :

- **Frontend** : `https://votre-site.netlify.app`
- **Backend** : `https://asma-rag-chatbot-2.onrender.com`
- **Health Check** : `https://asma-rag-chatbot-2.onrender.com/health`

---

## 📝 Checklist de Déploiement

- [ ] `script.js` pointe vers l'API Render
- [ ] `netlify.toml` créé
- [ ] Changements poussés sur GitHub
- [ ] Site créé sur Netlify
- [ ] Repository GitHub connecté
- [ ] Déploiement réussi
- [ ] Frontend testé et fonctionnel
- [ ] CORS vérifié
- [ ] Nom de domaine personnalisé (optionnel)

---

## 🎉 Félicitations !

Une fois déployé, votre chatbot sera accessible publiquement avec :
- ✅ Frontend rapide sur Netlify (CDN global)
- ✅ Backend intelligent sur Render (API RAG)
- ✅ Architecture professionnelle et scalable

**Profitez de votre chatbot en production !** 🤖✨