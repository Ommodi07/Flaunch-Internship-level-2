let micActive = false;
let lastBotResponse = "";
let userData = null;
let sessionId = null;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.interimResults = false;

function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9);
}

function submitRegistration() {
    const name = document.getElementById('userName').value.trim();
    const age = document.getElementById('userAge').value;
    const gender = document.getElementById('userGender').value;

    if (!name || !age || !gender) {
        alert('Please fill in all fields');
        return;
    }

    if (age < 1 || age > 120) {
        alert('Please enter a valid age between 1 and 120');
        return;
    }

    userData = {
        name: name,
        age: age,
        gender: gender
    };

    // Generate a new session ID
    sessionId = generateSessionId();

    // Hide registration overlay and show chat interface
    document.getElementById('registrationOverlay').classList.add('hidden');
    document.getElementById('chatInterface').classList.remove('hidden');

    // Add welcome message
    const chatContainer = document.getElementById('chat-container');
    const welcomeMessage = document.createElement('div');
    welcomeMessage.classList.add('bot-reply');
    welcomeMessage.innerText = `Welcome ${name}! I'm HealBot, your medical assistant. How can I help you today?`;
    chatContainer.appendChild(welcomeMessage);
}

// ... (keeping the mic-related functions unchanged) ...

async function getMedicalAdvice() {
    const query = document.getElementById('query').value;
    if (!query.trim()) {
        alert("Please enter a query.");
        return;
    }

    const chatContainer = document.getElementById('chat-container');
    const userMessage = document.createElement('div');
    userMessage.classList.add('user-message');
    userMessage.innerText = query;
    chatContainer.appendChild(userMessage);

    document.getElementById('loader').style.display = 'block';

    try {
        const response = await fetch('/get_medical_advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                userData: userData,
                sessionId: sessionId
            })
        });

        const data = await response.json();

        if (data.advice) {
            const botReply = document.createElement('div');
            botReply.classList.add('bot-reply');
            botReply.innerText = data.advice;
            chatContainer.appendChild(botReply);

            lastBotResponse = data.advice;

            // If server sent a new session ID, update it
            if (data.sessionId) {
                sessionId = data.sessionId;
            }
        } else if (data.error) {
            const botReply = document.createElement('div');
            botReply.classList.add('bot-reply');
            botReply.innerText = 'Error: ' + data.error;
            chatContainer.appendChild(botReply);
        }
    } catch (error) {
        console.error('Error:', error);
    }

    chatContainer.scrollTop = chatContainer.scrollHeight;
    document.getElementById('loader').style.display = 'none';
    document.getElementById('query').value = ''; // Clear input field after sending
}

// ... (keeping the listenToResponse function unchanged) ...

function startMicInput() {
    if (micActive) {
        stopMicInput();
        return;
    }

    micActive = true;
    recognition.lang = document.getElementById('language-selector').value;

    recognition.start();

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('query').value = transcript;
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        alert('There was an error with the microphone. Please try again.');
    };

    recognition.onend = () => {
        micActive = false;
        document.getElementById('start-mic-btn').textContent = 'Start Mic';
    };

    document.getElementById('start-mic-btn').textContent = 'Stop Mic';
}

function stopMicInput() {
    recognition.stop();
    micActive = false;
    document.getElementById('start-mic-btn').textContent = 'Start Mic';
}

function listenToResponse() {
    if (!lastBotResponse) {
        alert("No response available to listen to.");
        return;
    }

    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(lastBotResponse);
        utterance.lang = document.getElementById('language-selector').value;
        speechSynthesis.speak(utterance);
    } else {
        console.error("Text-to-Speech not supported in this browser.");
        alert("Your browser does not support text-to-speech.");
    }
}