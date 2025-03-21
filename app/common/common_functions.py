import re
from IPython.display import display, Audio
import winsound
import uuid
import hashlib



def retrieve_context(vector_store, question,k=4):
    results = vector_store.similarity_search(question, k)  # Retrieve top 4 matches
    return "\n".join([doc.page_content for doc in results])

def get_response_from_rag(chain, vector_store, question,k=10):
    retrieved_results= vector_store.similarity_search(question,k=k)
    print([i.metadata['page'] for i in retrieved_results])
    response = chain.invoke({"context":retrieved_results,"question":question})
    return response

def clean_response(response):
    """Removes <think>...</think> tags and their content from the response."""
    return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

# def run_tts(pipeline, text):
#     generator = pipeline(
#         text, voice='af_bella',
#         speed=1, split_pattern=r'\n+'
#     )
#     for i, (gs, ps, audio) in enumerate(generator):
#         # print(i)  # i => index
#         # print(gs) # gs => graphemes/text
#         # print(ps) # ps => phonemes
#         display(Audio(data=audio, rate=24000, autoplay=i==0))
#         sf.write(f'audio_samples/{i}.wav', audio, 24000) # save each audio file

# def play_audio():
#     audio_path = "audio_samples/0.wav"
#     # Play the sound (SND_FILENAME makes sure it is treated as a file)
#     winsound.PlaySound(audio_path, winsound.SND_FILENAME)

def generate_uuid_from_string(identifier):
    """Generate a deterministic UUID from a given string (e.g., email)."""
    namespace = uuid.UUID("12345678-1234-5678-1234-567812345678")  # Use a fixed namespace UUID
    return str(uuid.uuid5(namespace, identifier))

def get_or_create_user(collection, user_id=None):
    """Retrieve an existing user or create a new one using a UUID."""
    if user_id:
        user_id = generate_uuid_from_string(user_id)  # Convert user-provided ID to UUID
    else:
        user_id = str(uuid.uuid4())  # Generate a random UUID for new users

    user_data = collection.find_one({"user_id": user_id})

    if not user_data:
        collection.insert_one({"user_id": user_id, "chat_history": []})

    return user_id