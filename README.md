# 🎓 Tuteur Éducatif Personnalisé

Application de tutorat intelligent pour lycéens, spécialisée en Histoire-Géographie et SVT.

**🆓 100% GRATUIT - Utilise l'API Groq (pas besoin de carte bancaire !)**

## ✨ Fonctionnalités

### 📚 Chat Intelligent
- Conversations personnalisées avec un tuteur IA
- Explications adaptées au niveau lycée
- Historique des conversations sauvegardé
- Support pour Histoire-Géographie et SVT

### 📝 Quiz Interactifs
- Génération automatique de quiz personnalisés
- Choix du sujet, difficulté et nombre de questions
- Corrections détaillées avec explications
- Système de notation instantané

### 📊 Suivi de Progression
- Points et système de niveaux
- Badges de réussite
- Statistiques détaillées par matière
- Historique des performances

## 🚀 Installation Locale

### Prérequis
- Python 3.8+
- Un navigateur web moderne
- Une clé API Groq (100% GRATUIT)

### 1. Obtenir une Clé API Groq (GRATUITE) 🆓

1. Va sur https://console.groq.com/
2. Crée un compte (gratuit, pas besoin de carte bancaire)
3. Clique sur "API Keys" dans le menu
4. Clique sur "Create API Key"
5. Copie cette clé (elle commence par `gsk_...`)

### 2. Configuration Backend

```bash
# Dans le dossier tuteur-educatif/

# Installer les dépendances Python
cd backend
pip install -r requirements.txt

# OU si tu as des erreurs de permissions:
pip install -r requirements.txt --break-system-packages
```

### 3. Configuration de la Clé API

Ouvre le fichier `.env` à la racine du projet et remplace:
```
GROQ_API_KEY=your_groq_api_key_here
```
par ta vraie clé API:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

### 4. Lancer l'Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Le serveur démarre sur http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
# Ouvre index.html dans ton navigateur
# OU utilise un serveur local:
python -m http.server 8080
```
Ensuite va sur http://localhost:8080

## 🌐 Déploiement

### Option 1: Render (Recommandé - Gratuit)

#### Backend:
1. Crée un compte sur https://render.com
2. Clique "New +" → "Web Service"
3. Connecte ton repo GitHub ou uploade les fichiers
4. Configuration:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
5. Dans "Environment", ajoute:
   - `GROQ_API_KEY` = ta clé API Groq
6. Clique "Create Web Service"
7. Note l'URL (ex: https://tuteur-educatif.onrender.com)

#### Frontend:
1. Dans `frontend/app.js`, change:
```javascript
const API_URL = 'https://TON-URL-RENDER.onrender.com';
```
2. Déploie le frontend sur Render (nouveau "Static Site")
3. Ou utilise Netlify/Vercel pour le frontend

### Option 2: Railway (Alternative)

1. Va sur https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Sélectionne ton repo
4. Railway détecte automatiquement Python
5. Ajoute la variable d'environnement `GROQ_API_KEY`
6. Déploiement automatique !

### Option 3: Heroku

```bash
# Crée un fichier Procfile à la racine:
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT

# Puis:
heroku create tuteur-educatif-unique-name
heroku config:set GROQ_API_KEY=ta_cle_groq
git push heroku main
```

## 📁 Structure du Projet

```
tuteur-educatif/
├── backend/
│   ├── main.py              # Serveur FastAPI
│   ├── database.py          # Gestion SQLite
│   └── requirements.txt     # Dépendances Python
├── frontend/
│   ├── index.html          # Interface utilisateur
│   ├── style.css           # Design moderne
│   └── app.js              # Logique JavaScript
├── .env                    # Configuration (NE PAS COMMITER!)
├── .gitignore             # Fichiers à ignorer
└── README.md              # Ce fichier
```

## 🎨 Design

L'application utilise un design moderne avec:
- Gradient animé en arrière-plan
- Interface responsive (mobile-friendly)
- Animations fluides
- Thème cohérent et professionnel
- Police Inter pour une lisibilité optimale

## 🔧 Technologies

**Backend:**
- FastAPI (serveur web rapide)
- SQLite (base de données)
- Groq API (IA gratuite - Mixtral 8x7B)
- Python 3.8+

**Frontend:**
- HTML5, CSS3, JavaScript
- Design responsive
- Pas de framework (vanilla JS)

## 📊 Base de Données

SQLite est utilisé pour stocker:
- Historique des conversations
- Quiz générés
- Résultats et scores
- Progression des étudiants

La base de données se crée automatiquement au premier lancement.

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifie que tu es dans le bon dossier
cd backend

# Réinstalle les dépendances
pip install -r requirements.txt --force-reinstall
```

### "Module not found"
```bash
pip install fastapi uvicorn anthropic python-dotenv pydantic
```

### Le frontend ne se connecte pas au backend
1. Vérifie que le backend tourne sur http://localhost:8000
2. Regarde les erreurs dans la Console du navigateur (F12)
3. Vérifie que `API_URL` dans `app.js` est correct

### "Invalid API Key"
1. Vérifie que ta clé dans `.env` est correcte
2. Assure-toi que `.env` est dans le dossier racine
3. Redémarre le serveur après avoir modifié `.env`

## 📝 Exemples d'Utilisation

### Chat
- "Explique-moi la Révolution française"
- "Comment fonctionne la photosynthèse ?"
- "Quelles sont les causes de la Première Guerre mondiale ?"

### Quiz
- Sujet: "La tectonique des plaques"
- Sujet: "La monarchie absolue"
- Sujet: "La reproduction humaine"

## 🤝 Support

Si tu as des questions ou des problèmes:
1. Vérifie ce README
2. Regarde les logs du serveur
3. Consulte la documentation de FastAPI ou Anthropic

## 📜 Licence

Projet éducatif - Usage libre pour l'apprentissage

---

**Bon courage pour ta présentation ! 🚀**

## 🎯 Checklist Avant Rendu

- [ ] Backend installé et fonctionnel
- [ ] Clé API configurée
- [ ] Frontend se connecte au backend
- [ ] Chat fonctionne
- [ ] Quiz génère et corrige correctement
- [ ] Progression s'affiche
- [ ] Application déployée (si requis)
- [ ] README à jour
- [ ] Code commenté et propre

## 🌟 Points Forts à Mentionner

1. **IA Avancée**: Utilise Claude Sonnet 4, un des meilleurs modèles
2. **Design Professionnel**: Interface moderne et intuitive
3. **Fonctionnalités Complètes**: Chat, quiz, progression
4. **Personnalisation**: Adapté au niveau lycée
5. **Persistance**: Base de données pour sauvegarder tout
6. **Scalable**: Architecture prête pour ajout de fonctionnalités
7. **Code Propre**: Bien structuré et commenté
