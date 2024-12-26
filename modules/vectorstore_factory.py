from langchain.chains.question_answering import load_qa_chain
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import FAISS
from config import Config
import os

class FaissVectorStore:
    def __init__(self,emb_model,emb_path):
        # Load the FAISS index and documents
        self.vectorstore_faiss= FAISS.load_local(emb_path, emb_model,
                                            allow_dangerous_deserialization=True)
        self.vectorstore_wrapper = VectorStoreIndexWrapper(vectorstore=self.vectorstore_faiss)







