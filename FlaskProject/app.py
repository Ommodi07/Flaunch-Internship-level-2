from flask import Flask, render_template, request, jsonify
from langchain_groq import ChatGroq

app = Flask(__name__)

# Initialize Groq client
client = ChatGroq(
    api_key="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"
)

def get_groq_response(user_input):
    try:
        # Create the chat completion
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant. Provide concise medical advice in 4-5 lines including medication recommendations when appropriate. For non-medical queries, explain that you cannot assist."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0
        )

        # Extract the response content
        return chat_completion.choices[0].message.content
    except Exception as e:
        return "Error: " + str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    chat_history = []
    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input:
            response_content = get_groq_response(user_input)
            chat_history.append({"user": user_input, "bot": response_content})

    return render_template("index.html", chat_history=chat_history)

if __name__ == "__main__":
    app.run(debug=True)
