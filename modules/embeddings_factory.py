from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

class OpenAIEmbed:
    def __init__(self):
        self.embedding = OpenAIEmbeddings(
            model="text-embedding-3-large",
            dimensions=1024
        )

    def generate_embeddings(self,docs,emb_path):
        if not os.path.exists(emb_path):
            vectorstore_faiss = FAISS.from_documents(
                docs,
                self.embedding
            )

        #wrapperstore_faiss = VectorStoreIndexWrapper(vectorstore=vectorstore_faiss)
            vectorstore_faiss.save_local(emb_path)