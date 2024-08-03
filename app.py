
from flask import Flask, render_template, request, redirect, url_for, session

from flask_session import Session
from main import OpenAIBot
import os
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# List of users
users = {'amit': 'amit','akhilesh': 'akhilesh','akshay': 'akshay','anshu': 'anshu','ashutosh': 'ashutosh','dolly': 'dolly','harsh': 'harsh','hridendra': 'hridendra','pallav': 'pallav','pranav': 'pranav','rahul': 'rahul','shubham': 'shubham','shubhangi': 'shubhangi','surbhi': 'surbhi','yash': 'yash','zaira': 'zaira'}

# session_id = str(Session(app))
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))
# Session(app)

def get_conversation_filename():
    return f'conversation_{datetime.now().strftime("%Y_%m_%d")}.json'
file_name = get_conversation_filename()

def conversation_file():
    if not os.path.exists(file_name):
        # Create the file with an empty dictionary
        with open(file_name, 'w') as file:
            json.dump({}, file)
    
    with open(file_name, 'r') as file:
        conversation = json.load(file)
    return conversation

def save_chat(conversation_data):
    with open(file_name, 'w') as file:
        json.dump(conversation_data, file, indent=4)

    # def save_chat(session_id):
#     with open(file_name,"r") as file:

# # create_conversation_file
# def load_file(filename):
#     with open(filename, 'w') as file:
#         user_chat= json.load(file)  
#     # if os.path.exists(filename):
    #     with open(filename, 'r') as file:
    #         chatbot.conversation = json.load(file)
    # else:
    #     chatbot.conversation = []


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
                # filename = get_conversation_filename()
                # chatbot.conversation = load_conversation(filename).get(username, [])
                return redirect(url_for('index'))
            else:
                return 'Invalid username or password', 401
        return render_template('login.html')
    except Exception as e:
        print("error in login:",e)
        return "An error occurred", 500

"""
@app.route('/')
def index():
    # print("index:",session_id)
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    # session_id = str(uuid.uuid4())    
    return render_template('index.html')
"""
@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    """
    session_id = request.cookies.get('s_k')  # Get session key from cookies
    if not session_id:
        return 'No session key found', 400
    """
    # username = session['username']
    # Get Prompt from User  
    prompt = request.form['prompt']
    # User can stop the chat by sending 'End Chat' as a Prompt
    if prompt.upper() == 'END CHAT':
        return 'END CHAT'

    # Generate and Print the Response from ChatBot
    response = chatbot.generate_response(prompt)
    # conversation_file()
    # chatbot.save_conversation(get_conversation_filename(),session_id)  # Save conversation after generating response
    # Update the chatbot conversation
    conversation_data = conversation_file()
    
    session_id = session['username']
    if session_id not in conversation_data.keys():
        conversation_data[session_id] = []
    conversation_data[session_id].append({"prompt": prompt, "response": response})
    save_chat(conversation_data)

    return response
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
# @app.route('/save_conversation', methods=['POST'])
# def save_conversation():
#     filename = request.form.get('filename', get_conversation_filename())
#     chatbot.save_conversation(filename)
#     return f"Conversation saved to {filename}"

# def save_conversation(self, filename,session_id):
#         try:
#             with open(filename, 'w') as file:
#                 user_chat= json.load(file)
#                 json.dump(self.conversation, user_chat[session_id], indent=4)
#             # logger.info(f"Conversation saved to {filename}")
#         except Exception as e:
#             # logger.error(f"Failed to save conversation: {e}")
#             print(e)
if __name__ == '__main__':
    # filename = get_conversation_filename()
    # load_conversation(filename)  # Load the previous conversation if the file exists
    app.run(debug=True, host='0.0.0.0', port=5011)