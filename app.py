from flask import Flask, render_template, request
from main import OpenAIBot
import os
app = Flask(__name__)
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Get Prompt from User  
    prompt = request.form['prompt']
    # User can stop the chat by sending 'End Chat' as a Prompt
    if prompt.upper() == 'END CHAT':
        return 'END CHAT'

    # Generate and Print the Response from ChatBot
    response = chatbot.generate_response(prompt)
    return response

if __name__ == '__main__':
    app.run(debug=True)