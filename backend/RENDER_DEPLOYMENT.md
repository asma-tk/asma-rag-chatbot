# 🚀 Guide de Déploiement sur Render

## Configuration Requise

### Variables d'Environnement à Configurer sur Render

Dans le dashboard Render, vous devez configurer les variables d'environnement suivantes :

#### 1. **GROQ_API_KEY** (OBLIGATOIRE) 🔑
- **Description** : Votre clé API Groq pour accéder au modèle LLM
- **Où l'obtenir** : https://console.groq.com/keys
- **Type** : Secret
- **Exemple** : `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 2. **GROQ_MODEL** (Déjà configuré) ✅
- **Valeur** : `llama-3.3-70b-versatile`
- **Description** : Modèle LLM utilisé par l'application
- **Note** : Déjà défini dans `render.yaml`

#### 3. **CHROMA_PERSIST_DIRECTORY** (Déjà configuré) ✅
- **Valeur** : `/opt/render/project/src/chroma_db`
- **Description** : Répertoire de persistance pour ChromaDB
- **Note** : Déjà défini dans `render.yaml`

#### 4. **PORT** (Automatique) ✅
- **Description** : Port assigné automatiquement par Render
- **Note** : Render fournit cette variable automatiquement

---

## 📋 Étapes de Déploiement

### 1. Préparer le Repository Git

```bash
# Vérifier que tous les fichiers sont commités
git status

# Ajouter les fichiers modifiés
git add Dockerfile render.yaml app.py runtime.txt .dockerignore

# Commiter les changements
git commit -m "Fix: Configuration pour déploiement Render"

# Pousser vers GitHub
git push origin main
```

### 2. Créer un Nouveau Service sur Render

1. Connectez-vous à https://dashboard.render.com
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repository GitHub
4. Sélectionnez le repository `chatbot`

### 3. Configuration du Service

Render détectera automatiquement le fichier `render.yaml`. Vérifiez que :

- **Name** : `chatbot-asma`
- **Environment** : `Docker`
- **Region** : `Frankfurt`
- **Branch** : `main`
- **Plan** : `Free`

### 4. Configurer les Variables d'Environnement

Dans l'onglet **"Environment"** :

1. Ajoutez `GROQ_API_KEY` :
   - Cliquez sur **"Add Environment Variable"**
   - Key : `GROQ_API_KEY`
   - Value : Votre clé API Groq
   - ✅ Cochez **"Secret"**

2. Les autres variables sont déjà dans `render.yaml` ✅

### 5. Déployer

1. Cliquez sur **"Create Web Service"**
2. Render va :
   - Cloner votre repository
   - Construire l'image Docker
   - Déployer l'application
   - Assigner une URL publique

### 6. Vérifier le Déploiement

Une fois déployé, testez :

```bash
# Health check
curl https://votre-app.onrender.com/health

# Devrait retourner :
# {"status":"healthy","chroma_documents":XX,"model":"llama-3.3-70b-versatile"}
```

---

## 🔍 Résolution de Problèmes

### Erreur : "GROQ_API_KEY non définie"

**Solution** : Vérifiez que la variable d'environnement est bien configurée dans Render :
1. Allez dans **Environment** → **Environment Variables**
2. Vérifiez que `GROQ_API_KEY` existe et contient votre clé

### Erreur : "Port already in use"

**Solution** : C'est normal en local. Sur Render, le port est géré automatiquement.

### Build Docker échoue

**Solution** : Vérifiez les logs de build dans Render :
1. Allez dans **Logs** → **Build Logs**
2. Cherchez les erreurs de dépendances
3. Vérifiez que `requirements.txt` est correct

### Application ne démarre pas

**Solution** : Vérifiez les logs d'exécution :
1. Allez dans **Logs** → **Deploy Logs**
2. Cherchez les erreurs Python
3. Vérifiez que tous les fichiers nécessaires sont présents (`data.txt`, etc.)

### ChromaDB ne persiste pas

**Solution** : Sur le plan gratuit de Render, le système de fichiers est éphémère.
- La base ChromaDB sera recréée à chaque déploiement
- C'est normal et attendu
- Les données sont rechargées depuis `data.txt` au démarrage

---

## 📊 Monitoring

### Endpoints de Santé

- **Health Check** : `GET /health`
  - Vérifie que l'application fonctionne
  - Retourne le nombre de documents indexés

- **Stats** : `GET /stats`
  - Statistiques du système
  - Modèles utilisés

### Logs

Accédez aux logs en temps réel :
1. Dashboard Render → Votre service
2. Onglet **"Logs"**
3. Filtrez par type : Build, Deploy, ou Runtime

---

## 🔒 Sécurité

### ✅ Bonnes Pratiques Appliquées

- ✅ Clé API stockée comme secret
- ✅ `.env` dans `.gitignore`
- ✅ CORS configuré (à restreindre en production)
- ✅ Variables d'environnement pour configuration

### ⚠️ Recommandations Supplémentaires

Pour la production :
1. **Restreindre CORS** : Limitez les origines autorisées
2. **Rate Limiting** : Ajoutez une limite de requêtes
3. **HTTPS** : Activé automatiquement par Render ✅
4. **Monitoring** : Configurez des alertes

---

## 💰 Coûts

### Plan Gratuit Render
- ✅ 750 heures/mois
- ✅ Mise en veille après 15 min d'inactivité
- ✅ Réveil automatique à la première requête
- ⚠️ Temps de réveil : ~30 secondes

### API Groq
- ✅ Gratuit pour usage modéré
- Vérifiez les limites : https://console.groq.com/settings/limits

---

## 🎯 URL de l'Application

Après déploiement, votre chatbot sera accessible à :
```
https://chatbot-asma.onrender.com
```

---

## 📞 Support

En cas de problème :
1. Vérifiez les logs Render
2. Consultez la documentation : https://render.com/docs
3. Vérifiez que `GROQ_API_KEY` est valide

---

**Dernière mise à jour** : 2026-05-24
**Version** : 1.0.0