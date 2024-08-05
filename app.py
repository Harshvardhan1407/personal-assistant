from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from main import OpenAIBot
import os
from datetime import datetime
import json

app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# List of users
users = {'amit': 'amit','akhilesh': 'akhilesh','akshay': 'akshay','anshu': 'anshu','ashutosh': 'ashutosh','dolly': 'dolly','harsh': 'harsh','hridendra': 'hridendra','pallav': 'pallav','pranav': 'pranav','rahul': 'rahul','shubham': 'shubham','shubhangi': 'shubhangi','surbhi': 'surbhi','yash': 'yash','zaira': 'zaira'}

# session_id = str(Session(app))
chatbot = OpenAIBot(os.getenv("GPT_MODEL"))
# Session(app)

def get_conversation_filename():
    return f'conversation_{datetime.now().strftime("%Y_%m_%d")}.json'

def load_conversation(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
                # if username in data.keys():
                #     print("here1")
                #     return data[username] #data[username]
                # print("here2")
                # return {} #json.load(file)
        else:
            with open(filename,"w") as file:
                json.dump({}, file)
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
        print(session['username'])
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
                # print(session['username'])
                filename = get_conversation_filename()
                main_conversation = load_conversation(filename)
                if username in main_conversation.keys():
                    chatbot.conversation = main_conversation[username]
                # else:
                #     chatbot.conversation = []
                return redirect(url_for('index'))
            else:
                return 'Invalid username or password', 401
        return render_template('login.html')
    except Exception as e:
        print("error in login:",e)
        return "An error occurred", 500

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        return redirect(url_for('login'))
    except Exception as e:
        print("error in logout:",e)

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    """
    session_id = request.cookies.get('s_k')  # Get session key from cookies
    if not session_id:
        return 'No session key found', 400
    """
    username = session['username']
    print(session['username'])
    # Get Prompt from User  
    prompt = request.form['prompt']
    # User can stop the chat by sending 'End Chat' as a Prompt
    if prompt.upper() == 'END CHAT':
        return 'END CHAT'
    response = chatbot.generate_response(prompt)

    filename = get_conversation_filename()
    conversation_data = load_conversation(filename)
    # print(conversation_data)
    # print(conversation_data.keys())
    # print("conversation:", conversation_data)
    # print("type",type(conversation_data))
    # if type(conversation_data) == dict:
    if username not in conversation_data.keys():
        conversation_data[username] = []
        conversation_data[username].append({"prompt": prompt, "response": response})
    else:
        conversation_data[username].append({"prompt": prompt, "response": response})
    # Save the updated conversation data
    save_conversation(filename, conversation_data)
    return response
    """
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
    """
if __name__ == '__main__':
    # filename = get_conversation_filename()
    # load_conversation(filename)  # Load the previous conversation if the file exists
    app.run(debug=True, host='0.0.0.0', port=5011)