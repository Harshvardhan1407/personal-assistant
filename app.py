from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from main import OpenAIBot
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
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
    # Get Prompt from User  
    prompt = request.form['prompt']
    # User can stop the chat by sending 'End Chat' as a Prompt
    if prompt.upper() == 'END CHAT':
        return 'END CHAT'

    # Generate and Print the Response from ChatBot
    response = chatbot.generate_response(prompt)
    # chatbot.save_conversation(get_conversation_filename())  # Save conversation after generating response
    return response

@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    filename = request.form.get('filename', get_conversation_filename())
    chatbot.save_conversation(filename)
    return f"Conversation saved to {filename}"

if __name__ == '__main__':
    filename = get_conversation_filename()
    # load_conversation(filename)  # Load the previous conversation if the file exists
    app.run(debug=True, host='0.0.0.0', port=5011)