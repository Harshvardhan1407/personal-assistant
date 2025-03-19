import streamlit as st
from app.utils.main_chatbot import CHATBOT
from common.common_functions import clean_response, get_response, retrieve_context
# Streamlit UI
st.set_page_config(page_title="JARVIS", layout="centered")
st.title("🦄 Hi Mr Stark")
st.write("Welcome to the chatbot! Feel free to ask me anything.")

#chatbot initialization
chatbot = CHATBOT()
chain, vector_store = chatbot.initilise_chatbot()
print("chatbot initialized")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.text_input("You:", key="input_text")

# Chat Functionality
if user_input:
    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    print("user_input",user_input)
    # Get response from the model
    with st.spinner("Thinking..."):
        try:
            response = get_response(chain, vector_store, user_input)
            # response = chain.invoke({"context":[],"question":user_input})  # Call the language model
            bot_response = clean_response(response)
        except Exception as e:
            bot_response = f"An error occurred: {str(e)}"

    # Append bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Display the conversation
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Bot:** {msg['content']}")

# Clear chat
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
