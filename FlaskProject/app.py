from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key='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')

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
    user_query = request.json.get('query', '')

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You have to give medical advice to the user . You have to consult the user Problems which can be related to physical as well as mental health. Provide concise medical advice in 4-5 lines including medication recommendations when needed. For non-medical queries, explain that you cannot assist. if user ask about your name, you have to say 'I am HealBot, your medical assistant'.If user greets you, you have to greet them back without medical advice."
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
        medical_advice = chat_completion.choices[0].message.content
        return jsonify({"advice": medical_advice})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
