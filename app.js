// Main application logic
let currentQuestionIndex = 0;
let userAnswers = [];

// DOM elements
const introSection = document.getElementById('intro');
const questionsSection = document.getElementById('questions');
const resultsSection = document.getElementById('results');
const startButton = document.getElementById('start-button');
const questionTitle = document.getElementById('question-title');
const questionDescription = document.getElementById('question-description');
const currentQuestionSpan = document.getElementById('current-question');
const totalQuestionsSpan = document.getElementById('total-questions');
const progressBar = document.getElementById('progress');
const resultsContainer = document.getElementById('results-container');
const restartButton = document.getElementById('restart-button');
const shareButton = document.getElementById('share-button');
const voteBtns = document.querySelectorAll('.vote-btn');

// Initialize
function init() {
    totalQuestionsSpan.textContent = moties.length;
    startButton.addEventListener('click', startQuiz);
    restartButton.addEventListener('click', restart);
    shareButton.addEventListener('click', shareResults);
    
    voteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const vote = e.currentTarget.dataset.vote;
            handleVote(vote);
        });
    });
}

// Start the quiz
function startQuiz() {
    currentQuestionIndex = 0;
    userAnswers = [];
    introSection.classList.add('hidden');
    questionsSection.classList.remove('hidden');
    showQuestion();
}

// Display current question
function showQuestion() {
    const question = moties[currentQuestionIndex];
    questionTitle.textContent = question.title;
    questionDescription.textContent = question.description;
    currentQuestionSpan.textContent = currentQuestionIndex + 1;
    
    // Update progress bar
    const progress = ((currentQuestionIndex + 1) / moties.length) * 100;
    progressBar.style.width = progress + '%';
}

// Handle user vote
function handleVote(vote) {
    userAnswers.push({
        questionId: moties[currentQuestionIndex].id,
        vote: vote
    });
    
    currentQuestionIndex++;
    
    if (currentQuestionIndex < moties.length) {
        showQuestion();
    } else {
        showResults();
    }
}

// Calculate match percentages
function calculateResults() {
    const parties = {};
    
    // Initialize all parties
    Object.keys(moties[0].votes).forEach(party => {
        parties[party] = {
            matches: 0,
            total: 0
        };
    });
    
    // Calculate matches
    userAnswers.forEach(answer => {
        const question = moties.find(m => m.id === answer.questionId);
        
        Object.keys(question.votes).forEach(party => {
            const partyVote = question.votes[party];
            const userVote = answer.vote;
            
            // Don't count if user voted neutral
            if (userVote === 'neutraal') {
                return;
            }
            
            parties[party].total++;
            
            // Full match
            if (partyVote === userVote) {
                parties[party].matches += 1;
            }
            // Partial match (both are not opposing)
            else if (partyVote === 'neutraal') {
                parties[party].matches += 0.5;
            }
        });
    });
    
    // Calculate percentages
    const results = [];
    Object.keys(parties).forEach(party => {
        if (parties[party].total > 0) {
            const percentage = (parties[party].matches / parties[party].total) * 100;
            results.push({
                party: party,
                percentage: percentage
            });
        }
    });
    
    // Sort by percentage descending
    results.sort((a, b) => b.percentage - a.percentage);
    
    return results;
}

// Display results
function showResults() {
    questionsSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    const results = calculateResults();
    resultsContainer.innerHTML = '';
    
    results.forEach((result, index) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'party-result';
        
        // Color gradient based on ranking
        const hue = 210 - (index * 15); // Blue to purple gradient
        resultDiv.style.background = `linear-gradient(90deg, hsl(${hue}, 60%, 45%), transparent)`;
        
        resultDiv.innerHTML = `
            <span class="party-name">${result.party}</span>
            <span class="party-percentage">${Math.round(result.percentage)}%</span>
        `;
        
        resultsContainer.appendChild(resultDiv);
    });
}

// Restart quiz
function restart() {
    resultsSection.classList.add('hidden');
    introSection.classList.remove('hidden');
    currentQuestionIndex = 0;
    userAnswers = [];
    progressBar.style.width = '0%';
}

// Share results
function shareResults() {
    const results = calculateResults();
    const topParty = results[0];
    const shareText = `Ik match ${Math.round(topParty.percentage)}% met ${topParty.party} op de MotieeMatcher! Probeer het zelf op beta.motiematcher.nl`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Mijn MotieeMatcher resultaat',
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Resultaat gekopieerd naar klembord!');
        }).catch(err => {
            console.log('Error copying:', err);
            alert('Kon resultaat niet kopiëren. Probeer handmatig te delen.');
        });
    }
}

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
