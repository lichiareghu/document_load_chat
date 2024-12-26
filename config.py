import os
from modules.embeddings_factory import OpenAIEmbed

class Config:
    OPENAI_API_KEY = os.environ['openai_api_key']
    ASSISTANT_ID =  os.environ['assistant_id']
    UPLOAD_DIR = "uploaded_files"
    EMB_DIR = "embedding_files"
    MODEL_EMB = OpenAIEmbed()
    VECTORSTORE_NAME = "faiss"