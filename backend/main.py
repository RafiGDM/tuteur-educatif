from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import json
from database import Database
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Tuteur Éducatif Personnalisé")

# CORS pour permettre au frontend de communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de la base de données
db = Database()

# Configuration Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ ATTENTION: GROQ_API_KEY non trouvée dans .env")
else:
    print(f"✅ GROQ_API_KEY chargée: {GROQ_API_KEY[:20]}...")
    
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Modèle gratuit et performant  

# Modèles Pydantic
class ChatMessage(BaseModel):
    message: str
    subject: str  # "histoire_geo" ou "svt"
    student_level: str = "lycée"

class QuizRequest(BaseModel):
    subject: str
    topic: str
    difficulty: str = "moyen"
    num_questions: int = 5

class QuizAnswer(BaseModel):
    quiz_id: int
    answers: List[int]  # Liste des indices de réponses choisies

class StudentProgress(BaseModel):
    student_id: str = "default_student"

# Prompts système pour le tuteur
SYSTEM_PROMPTS = {
    "histoire_geo": """Tu es un tuteur expert en Histoire-Géographie pour lycéens français.
    
    Ton rôle :
    - Expliquer les concepts de manière claire et adaptée au niveau lycée
    - Utiliser des exemples concrets et des analogies
    - Encourager la réflexion critique
    - Adapter ton niveau de langage à l'élève
    - Être patient et bienveillant
    - Utiliser des dates, événements et personnages historiques précis
    
    Matières couvertes : Histoire (toutes périodes), Géographie (France, Europe, Monde), Géopolitique
    
    Réponds toujours en français de manière pédagogique.""",
    
    "svt": """Tu es un tuteur expert en Sciences de la Vie et de la Terre pour lycéens français.
    
    Ton rôle :
    - Expliquer les concepts scientifiques de manière accessible
    - Utiliser des schémas verbaux et des exemples du quotidien
    - Encourager la démarche scientifique et l'esprit critique
    - Adapter ton vocabulaire au niveau lycée
    - Être encourageant et pédagogue
    - Couvrir : Biologie, Géologie, Écologie, Génétique, etc.
    
    Réponds toujours en français de manière pédagogique."""
}

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API du Tuteur Éducatif Personnalisé",
        "version": "1.0.0",
        "subjects": ["histoire_geo", "svt"]
    }

@app.post("/chat")
async def chat_with_tutor(chat: ChatMessage):
    """Endpoint pour discuter avec le tuteur IA"""
    try:
        # Vérifier la clé API
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="Clé API Groq non configurée. Vérifie ton fichier .env")
        
        # Récupérer l'historique
        history = db.get_chat_history(chat.subject)
        
        # Préparer les messages pour Groq
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS.get(chat.subject, SYSTEM_PROMPTS["histoire_geo"])}
        ]
        
        for h in history[-10:]:  # Garder les 10 derniers messages
            messages.append({
                "role": h["role"],
                "content": h["content"]
            })
        
        # Ajouter le nouveau message
        messages.append({
            "role": "user",
            "content": chat.message
        })
        
        # Appel à Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        print(f"🔄 Envoi requête à Groq pour: {chat.message[:50]}...")
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        # Afficher l'erreur si problème
        if response.status_code != 200:
            error_detail = response.text
            print(f"❌ Erreur Groq API: {response.status_code} - {error_detail}")
            raise HTTPException(status_code=500, detail=f"Erreur Groq API: {error_detail}")
        
        result = response.json()
        assistant_response = result["choices"][0]["message"]["content"]
        
        print(f"✅ Réponse reçue de Groq: {assistant_response[:50]}...")
        
        # Sauvegarder dans l'historique
        db.save_message(chat.subject, "user", chat.message)
        db.save_message(chat.subject, "assistant", assistant_response)
        
        # Mettre à jour la progression
        db.update_progress(chat.subject, "interaction")
        
        return {
            "response": assistant_response,
            "subject": chat.subject,
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à Groq: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à l'API Groq: {str(e)}")
    except KeyError as e:
        print(f"❌ Erreur dans la réponse de Groq: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Format de réponse invalide: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/quiz/generate")
async def generate_quiz(quiz_req: QuizRequest):
    """Génère un quiz personnalisé"""
    try:
        prompt = f"""Génère un quiz de {quiz_req.num_questions} questions sur le thème : {quiz_req.topic}
        
        Matière : {quiz_req.subject}
        Niveau : Lycée
        Difficulté : {quiz_req.difficulty}
        
        Format de réponse STRICT (JSON) :
        {{
            "title": "Titre du quiz",
            "questions": [
                {{
                    "question": "Texte de la question",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Explication détaillée de la réponse"
                }}
            ]
        }}
        
        Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "Tu es un expert en création de quiz éducatifs. Réponds UNIQUEMENT en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.8
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        quiz_text = result["choices"][0]["message"]["content"].strip()
        
        # Nettoyer le JSON si nécessaire
        if quiz_text.startswith("```json"):
            quiz_text = quiz_text.split("```json")[1].split("```")[0].strip()
        elif quiz_text.startswith("```"):
            quiz_text = quiz_text.split("```")[1].split("```")[0].strip()
        
        quiz_data = json.loads(quiz_text)
        
        # Sauvegarder le quiz
        quiz_id = db.save_quiz(quiz_req.subject, quiz_req.topic, quiz_data)
        
        return {
            "quiz_id": quiz_id,
            "quiz": quiz_data,
            "subject": quiz_req.subject
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Erreur de format JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/quiz/submit")
async def submit_quiz(submission: QuizAnswer):
    """Soumet les réponses d'un quiz et calcule le score"""
    try:
        quiz = db.get_quiz(submission.quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz non trouvé")
        
        quiz_data = json.loads(quiz["quiz_data"])
        questions = quiz_data["questions"]
        
        # Calculer le score
        correct = 0
        results = []
        
        for i, user_answer in enumerate(submission.answers):
            is_correct = user_answer == questions[i]["correct_answer"]
            if is_correct:
                correct += 1
            
            results.append({
                "question": questions[i]["question"],
                "user_answer": questions[i]["options"][user_answer],
                "correct_answer": questions[i]["options"][questions[i]["correct_answer"]],
                "is_correct": is_correct,
                "explanation": questions[i]["explanation"]
            })
        
        score = (correct / len(questions)) * 100
        
        # Sauvegarder les résultats
        db.save_quiz_result(submission.quiz_id, quiz["subject"], score, correct, len(questions))
        
        # Mettre à jour la progression
        db.update_progress(quiz["subject"], "quiz_completed", score)
        
        return {
            "score": round(score, 2),
            "correct": correct,
            "total": len(questions),
            "results": results,
            "performance": "Excellent !" if score >= 80 else "Bien !" if score >= 60 else "Continue à t'entraîner !"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/progress/{subject}")
async def get_progress(subject: str):
    """Récupère la progression de l'étudiant"""
    try:
        stats = db.get_statistics(subject)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/history/{subject}")
async def get_history(subject: str, limit: int = 20):
    """Récupère l'historique des conversations"""
    try:
        history = db.get_chat_history(subject, limit)
        return {"history": history, "subject": subject}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.delete("/history/{subject}")
async def clear_history(subject: str):
    """Efface l'historique d'une matière"""
    try:
        db.clear_chat_history(subject)
        return {"message": f"Historique de {subject} effacé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/leaderboard")
async def get_leaderboard():
    """Récupère le classement global"""
    try:
        stats_hg = db.get_statistics("histoire_geo")
        stats_svt = db.get_statistics("svt")
        
        total_points = stats_hg["total_points"] + stats_svt["total_points"]
        total_quizzes = stats_hg["quizzes_completed"] + stats_svt["quizzes_completed"]
        
        badges = []
        if total_points >= 1000:
            badges.append({"name": "Expert", "icon": "🏆"})
        if total_points >= 500:
            badges.append({"name": "Avancé", "icon": "⭐"})
        if total_quizzes >= 10:
            badges.append({"name": "Persévérant", "icon": "💪"})
        if stats_hg["avg_score"] >= 80 or stats_svt["avg_score"] >= 80:
            badges.append({"name": "Excellent", "icon": "🎯"})
        
        return {
            "total_points": total_points,
            "total_quizzes": total_quizzes,
            "badges": badges,
            "subjects": {
                "histoire_geo": stats_hg,
                "svt": stats_svt
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)