from flask import Flask, render_template, request, jsonify, session
from groq import Groq
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize Groq client
client = Groq(api_key='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')

# Store chat histories in memory (for production, use a database)
chat_histories = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/services.html')
def services():
    return render_template('services.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/get_medical_advice', methods=['POST'])
def get_medical_advice():
    data = request.json
    user_query = data.get('query', '')
    user_data = data.get('userData', {})
    session_id = data.get('sessionId', '')  # Get session ID from frontend

    # Initialize chat history for new sessions
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # Get chat history for this session
    chat_history = chat_histories[session_id]

    try:
        # Include user data in the system message
        system_message = f"""You have to give medical advice to {user_data.get('name', 'the user')} 
        (Age: {user_data.get('age', 'unknown')}, Gender: {user_data.get('gender', 'unknown')}). 
        You have to consult the user Problems which can be related to physical as well as mental health. 
        Provide concise medical advice in 4-5 lines including medication recommendations when needed. 
        For non-medical queries, explain that you cannot assist. 
        if user ask about your name, you have to say 'I am HealBot, your medical assistant'.
        If user greets you, you have to greet them back without medical advice.
        
        Previous conversation context:
        {format_chat_history(chat_history)}"""

        messages = [
            {
                "role": "system",
                "content": system_message
            }
        ]

        # Add chat history to messages
        for msg in chat_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current query
        messages.append({
            "role": "user",
            "content": user_query
        })

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        medical_advice = chat_completion.choices[0].message.content

        # Update chat history
        chat_histories[session_id].append({
            "role": "user",
            "content": user_query
        })
        chat_histories[session_id].append({
            "role": "assistant",
            "content": medical_advice
        })

        # Keep only last 10 messages to prevent context from growing too large
        if len(chat_histories[session_id]) > 20:
            chat_histories[session_id] = chat_histories[session_id][-20:]

        return jsonify({
            "advice": medical_advice,
            "sessionId": session_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_chat_history(history):
    """Format chat history for system message context"""
    if not history:
        return "No previous conversation."
    
    formatted = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "HealBot"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n".join(formatted)

if __name__ == '__main__':
    app.run(debug=True)