from flask import Flask, render_template, request, redirect, url_for, session
from main import OpenAIBot
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Initialize the chatbot
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))

# List of users
users = {'amit': 'amit','akhilesh': 'akhilesh','akshay': 'akshay','anshu': 'anshu','ashutosh': 'ashutosh','dolly': 'dolly','harsh': 'harsh','hridendra': 'hridendra','pallav': 'pallav','pranav': 'pranav','rahul': 'rahul','shubham': 'shubham','shubhangi': 'shubhangi','surbhi': 'surbhi','yash': 'yash','zaira': 'zaira'}

def get_conversation_filename():
    return f'conversation_{datetime.now().strftime("%Y_%m_%d")}.json'

def load_conversation(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        return {}
    except Exception as e:
        print("error in load_conversation:",e)

def save_conversation(filename, conversation):
    try:
        with open(filename, 'w') as file:
            json.dump(conversation, file, indent=4)
    except Exception as e:
        print("error in save_conversation:",e)

@app.route('/')
def index():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('index.html')
    except Exception as e:
        print("error in index:",e)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username in users and users[username] == password:
                session['username'] = username
                filename = get_conversation_filename()
                chatbot.conversation = load_conversation(filename).get(username, [])
                return redirect(url_for('index'))
            else:
                return 'Invalid username or password', 401
        return render_template('login.html')
    except Exception as e:
        print("error in login:",e)

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        return redirect(url_for('login'))
    except Exception as e:
        print("error in logout:",e)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        
        username = session['username']
        prompt = request.form['prompt']
        if prompt.upper() == 'END CHAT':
            return 'END CHAT'
        print("done till here 0")

        response = chatbot.generate_response(prompt)
        print("done till here 1")
        # Update the chatbot conversation
        filename = get_conversation_filename()
        conversation_data = load_conversation(filename)
        if username not in conversation_data:
            conversation_data[username] = []
        conversation_data[username].append({"prompt": prompt, "response": response})
        
        # Save the updated conversation data
        save_conversation(filename, conversation_data)
        return response

    except Exception as e:
        print("error in chat response:",e)

@app.route('/save_conversation', methods=['POST'])
def save_conversation_route():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        
        username = session['username']
        filename = get_conversation_filename()
        conversation_data = load_conversation(filename)
        save_conversation(filename, conversation_data)
        return f"Conversation saved to {filename}"
    except Exception as e:
        print("error i save_conversation_route:",e)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
