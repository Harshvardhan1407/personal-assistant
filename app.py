from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from main import OpenAIBot, logger
import os
from datetime import datetime, timedelta
import json
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# List of users
users = {
    'amit': 'amit', 'akhilesh': 'akhilesh', 'akshay': 'akshay', 'anshu': 'anshu',
    'ashutosh': 'ashutosh', 'dolly': 'dolly', 'harsh': 'harsh', 'hridendra': 'hridendra',
    'pallav': 'pallav', 'pranav': 'pranav', 'rahul': 'rahul', 'shubham': 'shubham',
    'shubhangi': 'shubhangi', 'surbhi': 'surbhi', 'yash': 'yash', 'zaira': 'zaira'
}
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))

def get_conversation_filename():
    return f'conversation_{datetime.now().strftime("%Y_%m_%d")}.json'

def load_conversation(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                # logger.info(f"{filename} file found and loaded")
                return json.load(file)
            
        else:
            with open(filename, "w") as file:
                logger.info(f"{filename} file not found, creating a new file")
                json.dump({}, file)
            return {}                
    except Exception as e:
        logger.info("error in load_conversation:", e)
        return {}
    
def save_conversation(filename, conversation):
    try:
        with open(filename, 'w') as file:
            json.dump(conversation, file, indent=4)
    except Exception as e:
        logger.info("error in save_conversation:", e)

@app.route('/')
def index():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('index.html')
    except Exception as e:
        logger.info("error in index:", e)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username in users and users[username] == password:
                session['username'] = username
                filename = get_conversation_filename()
                main_conversation = load_conversation(filename)
                if username in main_conversation:
                    chatbot.conversations[username] = main_conversation[username]
                return redirect(url_for('index'))
            else:
                return 'Invalid username or password', 401
        return render_template('login.html')
    except Exception as e:
        logger.info("error in login:", e)
        return "An error occurred", 500

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        return redirect(url_for('login'))
    except Exception as e:
        logger.info("error in logout:", e)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if 'username' not in session:
            return redirect(url_for('login'))
            
        username = session['username']
        prompt = request.form['prompt']

        # User can stop the chat by sending 'End Chat' as a Prompt
        if prompt.upper() == 'END CHAT':
            return 'END CHAT'
        
        response = chatbot.generate_response(username, prompt)

        filename = get_conversation_filename()
        conversation_data = load_conversation(filename)
        if username not in conversation_data:
            conversation_data[username] = []
        conversation_data[username].append({"prompt": prompt, "response": response})
        
        # Save the updated conversation data
        save_conversation(filename, conversation_data)
        return response
    except Exception as e:
        logger.info("error in chat:",e)
        return "An error occurred", 500

# 14:31
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
