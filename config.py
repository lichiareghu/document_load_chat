import os
from modules.embeddings_factory import OpenAIEmbed

class Config:
    OPENAI_API_KEY = os.environ['openai_api_key']
    ASSISTANT_ID =  os.environ['assistant_id']
    UPLOAD_DIR = "uploaded_files"
    DOWNLOAD_DIR = "downloads"
    EMB_DIR = "embedding_files"
    MODEL_EMB = OpenAIEmbed()
    VECTORSTORE_NAME = "faiss"
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    GOOGLE_CSE_ID = os.environ['GOOGLE_CSE_ID']
    USER_AGENT = "user_alpha"