## chat bot using OpenAI api's 
conda activate genai
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
for /d /r . %d in (_pycache_) do @if exist "%d" rd /s /q "%d"