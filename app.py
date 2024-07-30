from flask import Flask, render_template, request
from main import OpenAIBot
import os
from datetime import datetime
import json

app = Flask(__name__)
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))

def get_conversation_filename():
    return f'conversation_{datetime.now().strftime("%Y_%m_%d")}.json'

def load_conversation(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            chatbot.conversation = json.load(file)
    else:
        chatbot.conversation = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form['prompt']
    if prompt.upper() == 'END CHAT':
        return 'END CHAT'

    response = chatbot.generate_response(prompt)
    chatbot.save_conversation(get_conversation_filename())  # Save conversation after generating response
    return response

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    filename = request.form.get('filename', get_conversation_filename())
    chatbot.save_conversation(filename)
    return f"Conversation saved to {filename}"

if __name__ == '__main__':
    filename = get_conversation_filename()
    load_conversation(filename)  # Load the previous conversation if the file exists
    app.run(debug=True, host='0.0.0.0', port=5001)
