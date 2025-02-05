# from logger import logger
import traceback
import asyncio  # Import asyncio to run async functions
from main_chatbot import CHATBOT
from common_functions import clean_response, retrieve_context, run_tts, play_audio,get_response_from_rag
from config_toolcall import tools
chatbot = CHATBOT()
chatbot_components = chatbot.initialize_chatbot()

while True:
    try:
        input_query = input("user query: ")
        if input_query == "end":
            break
        if "audio" in input_query:
            play_audio()
        response = chatbot_components['llm_with_tool'].invoke(input_query)
        print(f"content: {response.content}\ntool_call: {response.tool_calls} \nmessage: {response.response_metadata['message']}")
        
        
        if response.tool_calls and len(response.tool_calls) > 0:
            tool_call = response.tool_calls[0]  # Assuming one tool call
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"🔧 Tool to Execute: {tool_name} with args: {tool_args}")

            # Execute Tool Function Dynamically
            tool_dict  = {i['name']: i["function"] for i in tools}
            # print("too_dict:", tool_dict)
            if tool_name in tool_dict:
                # print("tool_name",tool_name)
                result = tool_dict[tool_name](**tool_args)
                if tool_name == "general_query":
                    result = chatbot_components['llm_model'].invoke(result['user_input']).content
                if tool_name == "retrieve_information":
                    result = get_response_from_rag(chatbot_components['rag_chain'],
                                                   chatbot_components['vector_store'],
                                                   question= result['user_input'],
                                                    )
                     
            else:
                result = "Error: Tool not found."

            print("AI response :", result)

        else:
            print("AI Response:", response.content)
    except Exception as e:
        print(f"error occured: {e}",)
        traceback.print_exc()  # This will print the full stack trace
