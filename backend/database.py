import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name="tuteur_educatif.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table pour l'historique des conversations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table pour les quiz
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                quiz_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table pour les résultats de quiz
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                score REAL NOT NULL,
                correct_answers INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)
        
        # Table pour la progression
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(self, subject, role, content):
        """Sauvegarde un message dans l'historique"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (subject, role, content) VALUES (?, ?, ?)",
            (subject, role, content)
        )
        conn.commit()
        conn.close()
    
    def get_chat_history(self, subject, limit=50):
        """Récupère l'historique des conversations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM chat_history WHERE subject = ? ORDER BY timestamp DESC LIMIT ?",
            (subject, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        # Inverser pour avoir l'ordre chronologique
        return [dict(row) for row in reversed(rows)]
    
    def clear_chat_history(self, subject):
        """Efface l'historique d'une matière"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE subject = ?", (subject,))
        conn.commit()
        conn.close()
    
    def save_quiz(self, subject, topic, quiz_data):
        """Sauvegarde un nouveau quiz"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quizzes (subject, topic, quiz_data) VALUES (?, ?, ?)",
            (subject, topic, json.dumps(quiz_data))
        )
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quiz_id
    
    def get_quiz(self, quiz_id):
        """Récupère un quiz par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def save_quiz_result(self, quiz_id, subject, score, correct, total):
        """Sauvegarde le résultat d'un quiz"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quiz_results (quiz_id, subject, score, correct_answers, total_questions) VALUES (?, ?, ?, ?, ?)",
            (quiz_id, subject, score, correct, total)
        )
        conn.commit()
        conn.close()
    
    def update_progress(self, subject, activity_type, score=None):
        """Met à jour la progression de l'étudiant"""
        # Système de points
        points = 0
        if activity_type == "interaction":
            points = 5
        elif activity_type == "quiz_completed":
            points = 10
            if score and score >= 80:
                points += 10  # Bonus pour excellent score
            elif score and score >= 60:
                points += 5   # Bonus pour bon score
        
        conn = self.get_connection()
        cursor = conn.cursor()
        details = json.dumps({"score": score}) if score else None
        cursor.execute(
            "INSERT INTO progress (subject, activity_type, points, details) VALUES (?, ?, ?, ?)",
            (subject, activity_type, points, details)
        )
        conn.commit()
        conn.close()
    
    def get_statistics(self, subject):
        """Récupère les statistiques d'une matière"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Points totaux
        cursor.execute(
            "SELECT COALESCE(SUM(points), 0) as total_points FROM progress WHERE subject = ?",
            (subject,)
        )
        total_points = cursor.fetchone()["total_points"]
        
        # Nombre d'interactions
        cursor.execute(
            "SELECT COUNT(*) as count FROM progress WHERE subject = ? AND activity_type = 'interaction'",
            (subject,)
        )
        interactions = cursor.fetchone()["count"]
        
        # Quiz complétés
        cursor.execute(
            "SELECT COUNT(*) as count FROM quiz_results WHERE subject = ?",
            (subject,)
        )
        quizzes_completed = cursor.fetchone()["count"]
        
        # Score moyen
        cursor.execute(
            "SELECT COALESCE(AVG(score), 0) as avg_score FROM quiz_results WHERE subject = ?",
            (subject,)
        )
        avg_score = cursor.fetchone()["avg_score"]
        
        # Meilleur score
        cursor.execute(
            "SELECT COALESCE(MAX(score), 0) as best_score FROM quiz_results WHERE subject = ?",
            (subject,)
        )
        best_score = cursor.fetchone()["best_score"]
        
        # Derniers quiz
        cursor.execute(
            """SELECT qr.score, qr.completed_at, q.topic 
               FROM quiz_results qr 
               JOIN quizzes q ON qr.quiz_id = q.id 
               WHERE qr.subject = ? 
               ORDER BY qr.completed_at DESC 
               LIMIT 5""",
            (subject,)
        )
        recent_quizzes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "subject": subject,
            "total_points": total_points,
            "interactions": interactions,
            "quizzes_completed": quizzes_completed,
            "avg_score": round(avg_score, 2),
            "best_score": round(best_score, 2),
            "recent_quizzes": recent_quizzes,
            "level": self._calculate_level(total_points)
        }
    
    def _calculate_level(self, points):
        """Calcule le niveau basé sur les points"""
        if points >= 1000:
            return {"name": "Expert", "icon": "🏆"}
        elif points >= 500:
            return {"name": "Avancé", "icon": "⭐"}
        elif points >= 200:
            return {"name": "Intermédiaire", "icon": "📚"}
        elif points >= 50:
            return {"name": "Débutant+", "icon": "🌱"}
        else:
            return {"name": "Débutant", "icon": "🔰"}
