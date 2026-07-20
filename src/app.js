// APP STATE
let state = {
    mode: 'landing', // 'landing', 'practice', 'exam', 'study'
    questions: [], // The main database of questions
    currentIndex: 0, // Current index in practice or exam mode
    
    // Practice mode state
    practiceProgress: 0, // Saved index from localStorage
    
    // Exam mode state
    examQuestions: [], // 10 random questions chosen for the exam
    examAnswers: {}, // Map of { questionIndex: chosenOptionIndex }
    examTimeRemaining: 3600, // 60 minutes in seconds
    examTimerId: null,
    examStartTime: 0,
    
    // Stats and Bookmarks
    stats: {
        answered: 0,
        correct: 0,
        wrong: 0,
        history: {} // Map of { questionId: { correct: boolean, answeredIndex: number } }
    },
    bookmarks: [] // Array of question IDs
};

// INITIALIZE APP
document.addEventListener('DOMContentLoaded', () => {
    // Load question database from global QUESTIONS_DATA (loaded in questions_data.js)
    if (typeof QUESTIONS_DATA !== 'undefined') {
        state.questions = QUESTIONS_DATA.preguntas || [];
        document.getElementById('total-db-count').textContent = state.questions.length;
    } else {
        console.error("QUESTIONS_DATA could not be loaded!");
    }
    
    // Load local storage data
    loadLocalStorage();
    
    // Update dashboard statistics
    updateDashboardStats();
    
    // Set up search and filter event listeners for study bank
    document.getElementById('study-search').addEventListener('input', filterStudyBank);
    document.getElementById('study-bookmark-filter').addEventListener('change', filterStudyBank);
});

// LOCAL STORAGE MANAGEMENT
function loadLocalStorage() {
    // Load bookmarks
    const savedBookmarks = localStorage.getItem('unemi_poo_bookmarks');
    if (savedBookmarks) {
        state.bookmarks = JSON.parse(savedBookmarks);
    }
    
    // Load stats
    const savedStats = localStorage.getItem('unemi_poo_stats');
    if (savedStats) {
        state.stats = JSON.parse(savedStats);
    }
    
    // Load practice index progress
    const savedIndex = localStorage.getItem('unemi_poo_practice_index');
    if (savedIndex) {
        state.practiceProgress = parseInt(savedIndex, 10);
    }
}

function saveStatsToLocalStorage() {
    localStorage.setItem('unemi_poo_stats', JSON.stringify(state.stats));
}

function saveBookmarksToLocalStorage() {
    localStorage.setItem('unemi_poo_bookmarks', JSON.stringify(state.bookmarks));
}

function savePracticeProgress(index) {
    state.practiceProgress = index;
    localStorage.setItem('unemi_poo_practice_index', index.toString());
}

// UPDATE DASHBOARD STATS
function updateDashboardStats() {
    document.getElementById('stats-answered').textContent = state.stats.answered;
    document.getElementById('stats-correct').textContent = state.stats.correct;
    document.getElementById('stats-wrong').textContent = state.stats.wrong;
    document.getElementById('stats-bookmarks').textContent = state.bookmarks.length;
    
    // Calculate percentage completed
    if (state.questions.length > 0) {
        const completedPct = Math.round((state.stats.answered / state.questions.length) * 100);
        document.getElementById('stats-percentage').textContent = `${completedPct}%`;
    }
}

// RESET PROGRESS
function resetAllProgress() {
    if (confirm("¿Estás seguro de que deseas restablecer todo tu progreso? Esto borrará tu historial de respuestas, favoritos y progreso de práctica.")) {
        state.stats = {
            answered: 0,
            correct: 0,
            wrong: 0,
            history: {}
        };
        state.bookmarks = [];
        state.practiceProgress = 0;
        
        saveStatsToLocalStorage();
        saveBookmarksToLocalStorage();
        savePracticeProgress(0);
        updateDashboardStats();
        
        alert("Progreso restablecido correctamente.");
    }
}

// NAVIGATION
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
    
    // Scroll back to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function exitQuiz() {
    // Stop exam timer if running
    if (state.examTimerId) {
        clearInterval(state.examTimerId);
        state.examTimerId = null;
    }
    
    state.mode = 'landing';
    updateDashboardStats();
    showScreen('screen-landing');
}

// --- MODE 1: PRACTICE ---
function startPracticeMode() {
    state.mode = 'practice';
    
    // Load last progress index
    state.currentIndex = state.practiceProgress;
    if (state.currentIndex >= state.questions.length) {
        state.currentIndex = 0;
    }
    
    document.getElementById('quiz-mode-title').textContent = "Modo Práctica Completa";
    document.getElementById('quiz-timer-container').classList.add('hidden');
    document.getElementById('btn-quiz-prev').classList.remove('hidden');
    
    loadQuizQuestion();
    showScreen('screen-quiz');
}

// --- MODE 2: EXAM ---
function startMockMode() {
    state.mode = 'exam';
    state.currentIndex = 0;
    state.examAnswers = {};
    
    // Select 10 random questions
    const shuffled = [...state.questions].sort(() => 0.5 - Math.random());
    state.examQuestions = shuffled.slice(0, 10);
    
    // Start countdown timer
    state.examTimeRemaining = 3600; // 60 minutes
    state.examStartTime = Date.now();
    document.getElementById('quiz-timer').textContent = "60:00";
    document.getElementById('quiz-timer-container').classList.remove('hidden');
    
    if (state.examTimerId) clearInterval(state.examTimerId);
    state.examTimerId = setInterval(updateExamTimer, 1000);
    
    document.getElementById('quiz-mode-title').textContent = "Simulacro de Examen";
    
    // In Mock Exam mode, disable back button to mimic Moodle's sequential navigation lock
    const prevBtn = document.getElementById('btn-quiz-prev');
    prevBtn.classList.add('hidden');
    
    loadQuizQuestion();
    showScreen('screen-quiz');
}

function updateExamTimer() {
    state.examTimeRemaining--;
    
    if (state.examTimeRemaining <= 0) {
        clearInterval(state.examTimerId);
        state.examTimerId = null;
        alert("¡El tiempo del examen ha finalizado!");
        submitExam();
        return;
    }
    
    const minutes = Math.floor(state.examTimeRemaining / 60);
    const seconds = state.examTimeRemaining % 60;
    document.getElementById('quiz-timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// --- LOAD QUIZ QUESTION ---
function loadQuizQuestion() {
    const qList = state.mode === 'exam' ? state.examQuestions : state.questions;
    const currentQ = qList[state.currentIndex];
    
    if (!currentQ) return;
    
    // Update progress texts
    const totalQ = qList.length;
    document.getElementById('quiz-progress-text').textContent = `Pregunta ${state.currentIndex + 1} de ${totalQ}`;
    
    const progressPct = ((state.currentIndex + 1) / totalQ) * 100;
    document.getElementById('quiz-progress-bar').style.width = `${progressPct}%`;
    
    // Load Question Image
    const imgEl = document.getElementById('question-img');
    imgEl.src = currentQ.image_path;
    
    // Load Bookmark state
    const bookmarkBtn = document.getElementById('btn-bookmark-toggle');
    const bookmarkText = document.getElementById('bookmark-status-text');
    if (state.bookmarks.includes(currentQ.id)) {
        bookmarkBtn.classList.add('active');
        bookmarkText.textContent = "Favorito";
    } else {
        bookmarkBtn.classList.remove('active');
        bookmarkText.textContent = "Guardar en Favoritos";
    }
    
    // Hide feedback box by default
    const feedbackBox = document.getElementById('quiz-feedback-box');
    feedbackBox.classList.add('hidden');
    
    // Build options list
    const optionsContainer = document.getElementById('quiz-options-list');
    optionsContainer.innerHTML = '';
    
    // Define letters
    const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
    
    // Check if user has already answered this question in this session/history (Practice Mode)
    let practiceAnswer = null;
    if (state.mode === 'practice') {
        practiceAnswer = state.stats.history[currentQ.id];
    }
    
    // In Exam Mode, check if already answered
    const examAnswer = state.examAnswers[state.currentIndex];
    
    currentQ.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-item';
        btn.innerHTML = `
            <span class="option-letter">${letters[idx]}</span>
            <span class="option-text">${opt}</span>
        `;
        
        // Handle option click
        btn.addEventListener('click', () => handleOptionSelection(idx));
        
        optionsContainer.appendChild(btn);
    });
    
    // Disable/Enable Anterior button
    const prevBtn = document.getElementById('btn-quiz-prev');
    if (state.mode === 'practice') {
        prevBtn.disabled = state.currentIndex === 0;
    }
    
    // Next Button setup
    const nextBtn = document.getElementById('btn-quiz-next');
    if (state.currentIndex === totalQ - 1) {
        nextBtn.textContent = state.mode === 'exam' ? 'Terminar Intento' : 'Finalizar Práctica';
    } else {
        nextBtn.textContent = 'Siguiente';
    }
    
    // Re-apply states if previously answered
    if (state.mode === 'practice' && practiceAnswer) {
        revealPracticeAnswer(practiceAnswer.answeredIndex, currentQ.correct_index);
    } else if (state.mode === 'exam' && examAnswer !== undefined) {
        // Highlight chosen option in exam mode (no correct/incorrect colors shown yet)
        const items = optionsContainer.querySelectorAll('.option-item');
        if (items[examAnswer]) {
            items[examAnswer].classList.add('selected');
        }
    }
}

// --- OPTION SELECTION ---
function handleOptionSelection(chosenIdx) {
    const qList = state.mode === 'exam' ? state.examQuestions : state.questions;
    const currentQ = qList[state.currentIndex];
    
    if (state.mode === 'practice') {
        // In practice mode, check if already answered. If so, do not allow changes.
        if (state.stats.history[currentQ.id]) return;
        
        const isCorrect = (chosenIdx === currentQ.correct_index);
        
        // Update stats
        state.stats.answered++;
        if (isCorrect) {
            state.stats.correct++;
        } else {
            state.stats.wrong++;
        }
        
        // Save to question history
        state.stats.history[currentQ.id] = {
            correct: isCorrect,
            answeredIndex: chosenIdx
        };
        
        saveStatsToLocalStorage();
        revealPracticeAnswer(chosenIdx, currentQ.correct_index);
        
    } else if (state.mode === 'exam') {
        // In exam mode, simply record choice and highlight it visually
        state.examAnswers[state.currentIndex] = chosenIdx;
        
        const optionsContainer = document.getElementById('quiz-options-list');
        optionsContainer.querySelectorAll('.option-item').forEach((item, idx) => {
            if (idx === chosenIdx) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }
}

// REVEAL ANSWER IN PRACTICE MODE
function revealPracticeAnswer(chosenIdx, correctIdx) {
    const optionsContainer = document.getElementById('quiz-options-list');
    const items = optionsContainer.querySelectorAll('.option-item');
    const isCorrect = (chosenIdx === correctIdx);
    
    items.forEach((item, idx) => {
        // Disable click hover behavior
        item.style.cursor = 'default';
        
        if (idx === correctIdx) {
            item.classList.add('correct');
        } else if (idx === chosenIdx && !isCorrect) {
            item.classList.add('wrong');
        }
    });
    
    // Show feedback box
    const feedbackBox = document.getElementById('quiz-feedback-box');
    const badge = document.getElementById('feedback-result-badge');
    const msg = document.getElementById('feedback-message');
    
    feedbackBox.classList.remove('hidden');
    if (isCorrect) {
        feedbackBox.className = 'feedback-box correct-feedback';
        badge.textContent = "Correcto";
        msg.textContent = "¡Excelente! Has respondido de forma correcta.";
    } else {
        feedbackBox.className = 'feedback-box wrong-feedback';
        badge.textContent = "Incorrecto";
        const correctLetter = ['A', 'B', 'C', 'D', 'E'][correctIdx];
        msg.textContent = `La respuesta correcta es la opción ${correctLetter}: "${items[correctIdx].querySelector('.option-text').textContent}"`;
    }
}

// --- NAVIGATION ACTIONS ---
function handleNextClick() {
    const qList = state.mode === 'exam' ? state.examQuestions : state.questions;
    
    // Verify user has answered (Mock Exam: optional but recommended; Practice: must have answered to save progress)
    if (state.mode === 'practice') {
        const currentQ = qList[state.currentIndex];
        if (!state.stats.history[currentQ.id]) {
            alert("Por favor selecciona una respuesta antes de continuar.");
            return;
        }
    }
    
    if (state.currentIndex < qList.length - 1) {
        state.currentIndex++;
        if (state.mode === 'practice') {
            savePracticeProgress(state.currentIndex);
        }
        loadQuizQuestion();
    } else {
        // Final question
        if (state.mode === 'exam') {
            if (confirm("¿Estás seguro de que deseas finalizar e intentar enviar el simulacro?")) {
                submitExam();
            }
        } else {
            alert("¡Felicidades! Has completado el banco de preguntas. Puedes seguir repasando o realizar un simulacro de examen.");
            exitQuiz();
        }
    }
}

function prevQuestion() {
    if (state.mode === 'practice' && state.currentIndex > 0) {
        state.currentIndex--;
        savePracticeProgress(state.currentIndex);
        loadQuizQuestion();
    }
}

// --- BOOKMARKS ---
function toggleCurrentBookmark() {
    const qList = state.mode === 'exam' ? state.examQuestions : state.questions;
    const currentQ = qList[state.currentIndex];
    
    if (!currentQ) return;
    
    const bIndex = state.bookmarks.indexOf(currentQ.id);
    const bookmarkBtn = document.getElementById('btn-bookmark-toggle');
    const bookmarkText = document.getElementById('bookmark-status-text');
    
    if (bIndex > -1) {
        state.bookmarks.splice(bIndex, 1);
        bookmarkBtn.classList.remove('active');
        bookmarkText.textContent = "Guardar en Favoritos";
    } else {
        state.bookmarks.push(currentQ.id);
        bookmarkBtn.classList.add('active');
        bookmarkText.textContent = "Favorito";
    }
    
    saveBookmarksToLocalStorage();
}

function toggleStudyBookmark(qId, btnEl) {
    const bIndex = state.bookmarks.indexOf(qId);
    if (bIndex > -1) {
        state.bookmarks.splice(bIndex, 1);
        btnEl.classList.remove('active');
        btnEl.querySelector('span').textContent = "Guardar en Favoritos";
    } else {
        state.bookmarks.push(qId);
        btnEl.classList.add('active');
        btnEl.querySelector('span').textContent = "Favorito";
    }
    saveBookmarksToLocalStorage();
}

// --- SUBMIT EXAM ---
function submitExam() {
    if (state.examTimerId) {
        clearInterval(state.examTimerId);
        state.examTimerId = null;
    }
    
    let correctCount = 0;
    state.examQuestions.forEach((q, idx) => {
        const userChoice = state.examAnswers[idx];
        if (userChoice === q.correct_index) {
            correctCount++;
        }
    });
    
    const grade = (correctCount / 10) * 10;
    const timeSpentSec = 3600 - state.examTimeRemaining;
    const minutes = Math.floor(timeSpentSec / 60);
    const seconds = timeSpentSec % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Update Results UI
    document.getElementById('result-score').textContent = `${correctCount}/10`;
    document.getElementById('result-grade').textContent = `${grade.toFixed(2)} / 10.00`;
    document.getElementById('result-time').textContent = timeString;
    document.getElementById('result-pct').textContent = `${Math.round((correctCount/10)*100)}%`;
    
    // Build Review Cards
    const reviewContainer = document.getElementById('result-review-container');
    reviewContainer.innerHTML = '';
    
    const letters = ['A', 'B', 'C', 'D', 'E'];
    
    state.examQuestions.forEach((q, idx) => {
        const userChoice = state.examAnswers[idx];
        const isCorrect = (userChoice === q.correct_index);
        
        const card = document.createElement('div');
        card.className = 'review-card';
        
        const chosenText = userChoice !== undefined ? `${letters[userChoice]}: "${q.options[userChoice]}"` : "Sin responder";
        const correctText = `${letters[q.correct_index]}: "${q.options[q.correct_index]}"`;
        
        card.innerHTML = `
            <div class="review-card-header">
                <span class="study-card-index">Pregunta ${idx + 1}</span>
                <span class="feedback-badge ${isCorrect ? 'bg-success' : 'bg-danger'}">
                    ${isCorrect ? 'Correcta' : 'Incorrecta'}
                </span>
            </div>
            <div class="review-card-img">
                <img src="${q.image_path}" alt="Pregunta ${idx + 1}">
            </div>
            <div class="review-user-ans ${isCorrect ? 'bg-success' : 'bg-danger'}" style="background-color: ${isCorrect ? 'var(--success-bg)' : 'var(--danger-bg)'}; border: 1px solid ${isCorrect ? 'var(--success-border)' : 'var(--danger-border)'}">
                <strong>Tu elección:</strong> ${chosenText}
            </div>
            ${!isCorrect ? `
            <div class="review-correct-ans">
                <strong>Respuesta correcta:</strong> ${correctText}
            </div>` : ''}
        `;
        
        reviewContainer.appendChild(card);
    });
    
    showScreen('screen-results');
}

// --- MODE 3: STUDY BANK ---
function startStudyBankMode() {
    state.mode = 'study';
    renderStudyBank();
    showScreen('screen-study');
}

function renderStudyBank() {
    const container = document.getElementById('study-questions-container');
    container.innerHTML = '';
    
    const searchVal = document.getElementById('study-search').value.toLowerCase();
    const bookmarkFilter = document.getElementById('study-bookmark-filter').value;
    
    let filteredQuestions = state.questions.filter(q => {
        // Search filter
        const matchesSearch = q.text_snippet.toLowerCase().includes(searchVal);
        
        // Bookmark filter
        const matchesBookmark = (bookmarkFilter === 'all') || state.bookmarks.includes(q.id);
        
        return matchesSearch && matchesBookmark;
    });
    
    if (filteredQuestions.length === 0) {
        container.innerHTML = `<div class="welcome-box text-center" style="text-align: center; padding: 3rem;"><p>No se encontraron preguntas que coincidan con los filtros.</p></div>`;
        return;
    }
    
    const letters = ['A', 'B', 'C', 'D', 'E'];
    
    filteredQuestions.forEach((q, originalIdx) => {
        // Find index in main array
        const mainIdx = state.questions.findIndex(item => item.id === q.id);
        
        const card = document.createElement('div');
        card.className = 'study-card';
        
        const isBookmarked = state.bookmarks.includes(q.id);
        
        card.innerHTML = `
            <div class="study-card-left">
                <img src="${q.image_path}" alt="Pregunta ${mainIdx + 1}">
            </div>
            <div class="study-card-right">
                <div class="study-card-header">
                    <span class="study-card-index">Pregunta ${mainIdx + 1} de 125</span>
                    <button class="btn-bookmark ${isBookmarked ? 'active' : ''}" onclick="toggleStudyBookmark('${q.id}', this)">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.907c.961 0 1.371 1.24.588 1.81l-3.97 2.883a1 1 0 00-.364 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.971-2.883a1 1 0 00-1.18 0l-3.97 2.883c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.364-1.118l-3.97-2.883c-.783-.57-.372-1.81.587-1.81h4.907a1 1 0 00.95-.69l1.519-4.674z" />
                        </svg>
                        <span>${isBookmarked ? 'Favorito' : 'Guardar en Favoritos'}</span>
                    </button>
                </div>
                <div class="study-options">
                    ${q.options.map((opt, optIdx) => {
                        const isCorrect = (optIdx === q.correct_index);
                        return `
                            <div class="study-option-item ${isCorrect ? 'correct' : ''}">
                                <span class="option-letter">${letters[optIdx]}</span>
                                <span class="option-text">${opt}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function filterStudyBank() {
    renderStudyBank();
}
