// Configuration
const API_URL = 'https://tuteur-educatif.onrender.com';

let currentSubject = 'histoire_geo';
let currentQuizSubject = 'histoire_geo';
let currentQuizId = null;
let userAnswers = [];

// Éléments DOM
const navBtns = document.querySelectorAll('.nav-btn');
const sections = document.querySelectorAll('.section');
const subjectBtns = document.querySelectorAll('.subject-btn');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const loadingOverlay = document.getElementById('loading-overlay');

// Quiz elements
const subjectBtnsQuiz = document.querySelectorAll('.subject-btn-quiz');
const quizTopic = document.getElementById('quiz-topic');
const quizDifficulty = document.getElementById('quiz-difficulty');
const quizNumQuestions = document.getElementById('quiz-num-questions');
const generateQuizBtn = document.getElementById('generate-quiz-btn');
const quizGenerator = document.getElementById('quiz-generator');
const quizDisplay = document.getElementById('quiz-display');
const quizResults = document.getElementById('quiz-results');
const backToGeneratorBtn = document.getElementById('back-to-generator');
const submitQuizBtn = document.getElementById('submit-quiz-btn');
const newQuizBtn = document.getElementById('new-quiz-btn');

// ========== NAVIGATION ==========
navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const sectionId = btn.dataset.section;
        
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        sections.forEach(s => s.classList.remove('active'));
        document.getElementById(`${sectionId}-section`).classList.add('active');
        
        // Charger les données selon la section
        if (sectionId === 'progress') {
            loadProgress();
        }
    });
});

// ========== SUBJECT SELECTION (CHAT) ==========
subjectBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        currentSubject = btn.dataset.subject;
        subjectBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadChatHistory();
    });
});

// ========== SUBJECT SELECTION (QUIZ) ==========
subjectBtnsQuiz.forEach(btn => {
    btn.addEventListener('click', () => {
        currentQuizSubject = btn.dataset.subject;
        subjectBtnsQuiz.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// ========== CHAT FUNCTIONS ==========
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Désactiver l'input pendant l'envoi
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    // Afficher le message de l'utilisateur
    addMessage('user', message);
    chatInput.value = '';
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                subject: currentSubject,
                student_level: 'lycée'
            })
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de l\'envoi du message');
        }
        
        const data = await response.json();
        addMessage('assistant', data.response);
        
    } catch (error) {
        console.error('Erreur:', error);
        addMessage('assistant', '❌ Désolé, une erreur s\'est produite. Vérifie que le serveur est bien démarré.');
    } finally {
        showLoading(false);
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(role, content) {
    // Supprimer le message de bienvenue si présent
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (role === 'user') {
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
    }
    
    contentDiv.appendChild(time);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/history/${currentSubject}`);
        const data = await response.json();
        
        chatMessages.innerHTML = '';
        
        if (data.history.length === 0) {
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">👋</div>
                    <h2>Bonjour ! Je suis ton tuteur personnel</h2>
                    <p>Sélectionne une matière et pose-moi tes questions. Je suis là pour t'aider à réussir !</p>
                </div>
            `;
        } else {
            data.history.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error('Erreur lors du chargement de l\'historique:', error);
    }
}

async function clearHistory() {
    if (!confirm('Êtes-vous sûr de vouloir effacer l\'historique de cette matière ?')) {
        return;
    }
    
    try {
        showLoading(true);
        await fetch(`${API_URL}/history/${currentSubject}`, {
            method: 'DELETE'
        });
        loadChatHistory();
    } catch (error) {
        console.error('Erreur lors de l\'effacement de l\'historique:', error);
        alert('Erreur lors de l\'effacement de l\'historique');
    } finally {
        showLoading(false);
    }
}

// Event listeners pour le chat
sendBtn.addEventListener('click', sendMessage);
clearHistoryBtn.addEventListener('click', clearHistory);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize du textarea
chatInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

// ========== QUIZ FUNCTIONS ==========
async function generateQuiz() {
    const topic = quizTopic.value.trim();
    if (!topic) {
        alert('Veuillez entrer un sujet pour le quiz');
        return;
    }
    
    const difficulty = quizDifficulty.value;
    const numQuestions = parseInt(quizNumQuestions.value);
    
    try {
        showLoading(true);
        generateQuizBtn.disabled = true;
        
        const response = await fetch(`${API_URL}/quiz/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subject: currentQuizSubject,
                topic: topic,
                difficulty: difficulty,
                num_questions: numQuestions
            })
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la génération du quiz');
        }
        
        const data = await response.json();
        currentQuizId = data.quiz_id;
        displayQuiz(data.quiz);
        
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur lors de la génération du quiz. Vérifie que le serveur est bien démarré.');
    } finally {
        showLoading(false);
        generateQuizBtn.disabled = false;
    }
}

function displayQuiz(quiz) {
    document.getElementById('quiz-title').textContent = quiz.title;
    
    const questionsContainer = document.getElementById('quiz-questions');
    questionsContainer.innerHTML = '';
    userAnswers = [];
    
    quiz.questions.forEach((question, qIndex) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        
        questionDiv.innerHTML = `
            <div class="question-number">Question ${qIndex + 1}</div>
            <div class="question-text">${question.question}</div>
            <div class="question-options">
                ${question.options.map((option, oIndex) => `
                    <label class="option-label">
                        <input type="radio" name="question-${qIndex}" value="${oIndex}">
                        <span>${option}</span>
                    </label>
                `).join('')}
            </div>
        `;
        
        questionsContainer.appendChild(questionDiv);
    });
    
    quizGenerator.style.display = 'none';
    quizDisplay.style.display = 'block';
    quizResults.style.display = 'none';
}

async function submitQuiz() {
    // Récupérer les réponses
    userAnswers = [];
    const questions = document.querySelectorAll('.quiz-question');
    
    for (let i = 0; i < questions.length; i++) {
        const selected = document.querySelector(`input[name="question-${i}"]:checked`);
        if (!selected) {
            alert(`Veuillez répondre à la question ${i + 1}`);
            return;
        }
        userAnswers.push(parseInt(selected.value));
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_URL}/quiz/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quiz_id: currentQuizId,
                answers: userAnswers
            })
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la soumission du quiz');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur lors de la soumission du quiz');
    } finally {
        showLoading(false);
    }
}

function displayResults(results) {
    document.getElementById('results-score').textContent = `${results.score}%`;
    document.getElementById('results-performance').textContent = 
        `${results.correct}/${results.total} - ${results.performance}`;
    
    const detailsContainer = document.getElementById('results-details');
    detailsContainer.innerHTML = '';
    
    results.results.forEach((result, index) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${result.is_correct ? 'correct' : 'incorrect'}`;
        
        resultDiv.innerHTML = `
            <div class="result-question">
                <strong>Question ${index + 1}:</strong> ${result.question}
            </div>
            <div class="result-answer user">
                <strong>Ta réponse:</strong> ${result.user_answer}
                ${result.is_correct ? '✅' : '❌'}
            </div>
            ${!result.is_correct ? `
                <div class="result-answer correct-answer">
                    <strong>Bonne réponse:</strong> ${result.correct_answer}
                </div>
            ` : ''}
            <div class="result-explanation">
                <strong>💡 Explication:</strong> ${result.explanation}
            </div>
        `;
        
        detailsContainer.appendChild(resultDiv);
    });
    
    quizDisplay.style.display = 'none';
    quizResults.style.display = 'block';
}

function resetQuiz() {
    quizGenerator.style.display = 'block';
    quizDisplay.style.display = 'none';
    quizResults.style.display = 'none';
    quizTopic.value = '';
    currentQuizId = null;
    userAnswers = [];
}

// Event listeners pour le quiz
generateQuizBtn.addEventListener('click', generateQuiz);
submitQuizBtn.addEventListener('click', submitQuiz);
backToGeneratorBtn.addEventListener('click', resetQuiz);
newQuizBtn.addEventListener('click', resetQuiz);

// ========== PROGRESS FUNCTIONS ==========
async function loadProgress() {
    try {
        showLoading(true);
        
        // Charger le leaderboard global
        const leaderboardResponse = await fetch(`${API_URL}/leaderboard`);
        const leaderboard = await leaderboardResponse.json();
        
        // Mettre à jour les stats globales
        document.getElementById('total-points').textContent = leaderboard.total_points;
        document.getElementById('total-quizzes').textContent = leaderboard.total_quizzes;
        document.getElementById('level-name').textContent = 
            leaderboard.subjects.histoire_geo.level.name || 'Débutant';
        document.getElementById('badges-count').textContent = leaderboard.badges.length;
        
        // Afficher les badges
        const badgesContainer = document.getElementById('badges-container');
        if (leaderboard.badges.length > 0) {
            badgesContainer.innerHTML = leaderboard.badges.map(badge => `
                <div class="badge">
                    <span class="badge-icon">${badge.icon}</span>
                    <span>${badge.name}</span>
                </div>
            `).join('');
        } else {
            badgesContainer.innerHTML = '<p class="text-muted">Continue à apprendre pour débloquer des badges !</p>';
        }
        
        // Histoire-Géo
        const hgStats = leaderboard.subjects.histoire_geo;
        document.getElementById('hg-points').textContent = hgStats.total_points;
        document.getElementById('hg-quizzes').textContent = hgStats.quizzes_completed;
        document.getElementById('hg-avg').textContent = `${hgStats.avg_score}%`;
        document.getElementById('hg-best').textContent = `${hgStats.best_score}%`;
        
        const hgRecentContainer = document.getElementById('hg-recent');
        if (hgStats.recent_quizzes.length > 0) {
            hgRecentContainer.innerHTML = `
                <h4 style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.9rem;">Quiz récents</h4>
                ${hgStats.recent_quizzes.map(quiz => `
                    <div class="recent-quiz-item">
                        <span class="recent-quiz-topic">${quiz.topic}</span>
                        <span class="recent-quiz-score">${quiz.score}%</span>
                    </div>
                `).join('')}
            `;
        } else {
            hgRecentContainer.innerHTML = '<p class="text-muted">Aucun quiz complété</p>';
        }
        
        // SVT
        const svtStats = leaderboard.subjects.svt;
        document.getElementById('svt-points').textContent = svtStats.total_points;
        document.getElementById('svt-quizzes').textContent = svtStats.quizzes_completed;
        document.getElementById('svt-avg').textContent = `${svtStats.avg_score}%`;
        document.getElementById('svt-best').textContent = `${svtStats.best_score}%`;
        
        const svtRecentContainer = document.getElementById('svt-recent');
        if (svtStats.recent_quizzes.length > 0) {
            svtRecentContainer.innerHTML = `
                <h4 style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.9rem;">Quiz récents</h4>
                ${svtStats.recent_quizzes.map(quiz => `
                    <div class="recent-quiz-item">
                        <span class="recent-quiz-topic">${quiz.topic}</span>
                        <span class="recent-quiz-score">${quiz.score}%</span>
                    </div>
                `).join('')}
            `;
        } else {
            svtRecentContainer.innerHTML = '<p class="text-muted">Aucun quiz complété</p>';
        }
        
    } catch (error) {
        console.error('Erreur lors du chargement de la progression:', error);
        alert('❌ Erreur lors du chargement de la progression');
    } finally {
        showLoading(false);
    }
}

// ========== UTILITY FUNCTIONS ==========
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎓 Application Tuteur Éducatif chargée !');
    loadChatHistory();
});
