from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config_chatbot import embedding_model_name, vector_db_path3
file_path = r"C:\Users\HARSH\Downloads\JdVVNL_user_manual_2.pdf"

ollama_emb = OllamaEmbeddings(
    model=embedding_model_name,
)

pdf_loader = PyPDFLoader(file_path=file_path)
pdf_document = pdf_loader.load()
pdf_document.pop(2) # remove index page for better results
print("total_pages: ",len(pdf_document))

text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
split_pdf_documents= text_splitter.split_documents(pdf_document)
print(f"total chunks : {len(split_pdf_documents)}")

vector_db_path= vector_db_path3

vector_store = FAISS.from_documents(
    documents=split_pdf_documents,
    embedding=ollama_emb
)
vector_store.save_local(vector_db_path)


# loaded_vector_store = FAISS.load_local(
#     folder_path=vector_db_path,
#     embeddings=ollama_emb,
#     allow_dangerous_deserialization=True,
# )


query = "how many report are there ?"
retrieved_results=vector_store.similarity_search(query,k=10)
print(f"pages retrived: {[retrieved_results[i].metadata['page'] for i in range(len(retrieved_results))]}")
