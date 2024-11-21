let micActive = false;
let lastBotResponse = ""; // To store the latest bot response
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.interimResults = false;

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
        document.getElementById('query').value = transcript; // Set the text area to the recognized speech
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        alert('There was an error with the microphone. Please try again.');
    };

    recognition.onend = () => {
        micActive = false;
        document.getElementById('start-mic-btn').textContent = 'Start Mic'; // Reset the button text
    };

    document.getElementById('start-mic-btn').textContent = 'Stop Mic'; // Change the button text when mic is active
}

function stopMicInput() {
    recognition.stop(); // Stop the recognition when the button is pressed again
    micActive = false;
    document.getElementById('start-mic-btn').textContent = 'Start Mic'; // Reset the button text
}

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

    // Show loader
    document.getElementById('loader').style.display = 'block';

    try {
        const response = await fetch('/get_medical_advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.advice) {
            const botReply = document.createElement('div');
            botReply.classList.add('bot-reply');
            botReply.innerText = data.advice;
            chatContainer.appendChild(botReply);

            // Update the latest bot response
            lastBotResponse = data.advice;
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
}

// Text-to-Speech function for the latest response
function listenToResponse() {
    if (!lastBotResponse) {
        alert("No response available to listen to.");
        return;
    }

    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(lastBotResponse);
        utterance.lang = document.getElementById('language-selector').value; // Set language based on user's selection
        speechSynthesis.speak(utterance);
    } else {
        console.error("Text-to-Speech not supported in this browser.");
        alert("Your browser does not support text-to-speech.");
    }
}
