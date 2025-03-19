# from logger import logger
import traceback
import asyncio  # Import asyncio to run async functions
from utils.main_chatbot import CHATBOT
from common.common_functions import clean_response, retrieve_context, run_tts, play_audio,get_response_from_rag, get_or_create_user
from config.config_toolcall import chatbot_tools
tools = chatbot_tools.tools
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from database import mongo_collection
chatbot = CHATBOT()
chatbot_components = chatbot.initialize_chatbot()

# Get User ID
user_id = input("Enter your User ID:").strip()
user_session_id = get_or_create_user(mongo_collection, user_id)
# print(f"User Session ID: {user_session_id}")
def conversation_history(collection, user_session_id):
    # Fetch only the last 10 chat messages for the given user
    # user_chat_history = []
    user_chat_history = collection.find_one(
        {"user_id": user_session_id},
        {"chat_history": {"$slice": -10}}  # Fetch only the last 10 messages
    )
    print(f"user_chat_history: {len(user_chat_history['chat_history'])}")
    # print(user_chat_history)
    # Print the messages if they exist
    # if user_chat_history and "chat_history" in user_chat_history:
    #     for msg in user_chat_history["chat_history"]:
    #         print(msg)
    
    return user_chat_history

def user_conversation(collection, user_session_id, user_message):
    """Handle conversation and store messages in MongoDB."""
    user_chat_history = conversation_history(collection, user_session_id)

    # Retrieve or initialize chat history
    ongoing_conversation = user_chat_history.get("chat_history")

    # Append user message
    ongoing_conversation.append({"role": "user", "content": user_message})
    response = chatbot_components["llm_chain"].invoke({"history":ongoing_conversation,"question": user_message})        

    # Append AI response
    ongoing_conversation.append({"role": "assistant", "content": response})

    collection.update_one(
        {"user_id": user_session_id},
        {"$set": {"chat_history": ongoing_conversation}}
    )
    return response

while True:
    try:
        input_query = input("user query: ")
        if input_query == "end":
            break

        response = user_conversation(mongo_collection, user_session_id, input_query)
        # response = chatbot_components["llm_chain"].invoke({"question": input_query})        
        print("AI response :", response)

    except Exception as e:
        print(f"error occured: {e}",)
        traceback.print_exc()  # This will print the full stack trace





# print(tools)
# while True:
#     try:
#         input_query = input("user query: ")
#         if input_query == "end":
#             break
#         if "audio" in input_query:
#             play_audio()
#         response = chatbot_components['llm_with_tool'].invoke(input_query)
#         print(f"content: {response.content}\ntool_call: {response.tool_calls} \nmessage: {response.response_metadata['message']}")
           
#         if response.tool_calls and len(response.tool_calls) > 0:
#             tool_call = response.tool_calls[0]  # Assuming one tool call
#             tool_name = tool_call["name"]
#             tool_args = tool_call["args"]

#             print(f"🔧 Tool to Execute: {tool_name} with args: {tool_args}")

#             # Execute Tool Function Dynamically
#             tool_dict  = {i['name']: i["function"] for i in tools}
#             # print("too_dict:", tool_dict)
#             if tool_name in tool_dict:
#                 # print("tool_name",tool_name)
#                 result = tool_dict[tool_name](**tool_args)
#                 if tool_name == "general_query":
#                     result = chatbot_components['llm_model'].invoke(result['user_input']).content
#                 if tool_name == "retrieve_information":
#                     result = get_response_from_rag(chatbot_components['rag_chain'],
#                                                    chatbot_components['vector_store'],
#                                                    question= result['user_input'],
#                                                     )
                     
#             else:
#                 result = "Error: Tool not found."

#             print("AI response :", result)

#         else:
#             print("AI Response:", response.content)
#     except Exception as e:
#         print(f"error occured: {e}",)
#         traceback.print_exc()  # This will print the full stack trace
