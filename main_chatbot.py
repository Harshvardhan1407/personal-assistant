# import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from chatbot_prompt import rag_template
from config_chatbot import llm_model_name, embedding_model_name, vector_db_path
from config_toolcall import tools
# from kokoro import KPipeline


class CHATBOT:    
    def initialize_chatbot (self):
        # gateway model toolcall

        # chat_model 
        llm_model = ChatOllama(
            model= llm_model_name,
            )
        
        # embedding model
        ollama_emb = OllamaEmbeddings(
            model=embedding_model_name,
            )
        
        #vector store
        loaded_vector_store = FAISS.load_local(
            folder_path= vector_db_path,
            embeddings= ollama_emb,
            allow_dangerous_deserialization= True,
            )

        # # tts 
        # tts_pipeline = KPipeline(lang_code='a')

        prompt = ChatPromptTemplate.from_template(rag_template)
        rag_chain = prompt | llm_model | StrOutputParser()
        
        llm_with_tool = llm_model.bind_tools(tools)        
        
        chatbot_modules = {
            "llm_model": llm_model,
            "rag_chain": rag_chain,
            "vector_store": loaded_vector_store,
            # "tts_pipeline": tts_pipeline,
            "llm_with_tool": llm_with_tool,
        }
        return chatbot_modules

# chatbot = CHATBOT()
# llm_model, rag_chain, loaded_vector_store = chatbot.initilise_chatbot()
# query = "how many report are there ?"
# retrieved_results=loaded_vector_store.similarity_search(query,k=10)
# print(f"pages retrived: {[retrieved_results[i].metadata['page'] for i in range(len(retrieved_results))]}")

# response = rag_chain.invoke({"context":retrieved_results,"question":query})
# print(f"content: {response.content}\ntool_call: {response.tool_calls} \nmessage: {response.response_metadata['message']}")
# response = chain.invoke({"context":[],"question":"hi"})
# print("response",response)
# clean_response = response.replace("<think>", "").replace("</think>", "").strip()
# print("clean_response",clean_response)


