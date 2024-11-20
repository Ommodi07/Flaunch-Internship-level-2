from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key='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')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_medical_advice', methods=['POST'])
def get_medical_advice():
    # Get the user's medical query from the request
    user_query = request.json.get('query', '')
    
    try:
        # Create chat completion with Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant and you name is HealBot. Provide concise medical advice in 4-5 lines including medication recommendations when appropriate. For non-medical queries, explain that you cannot assist."
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        # Extract and return the response
        medical_advice = chat_completion.choices[0].message.content
        return jsonify({"advice": medical_advice})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)