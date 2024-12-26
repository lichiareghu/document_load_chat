import logging

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader
from config import Config
import os
from modules.utils import create_name

class PreprocessPipeline:
    def __init__(self,emb_model):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
        self.emb_model = emb_model

    def load_documents(self,filepath):
        loader = PyPDFLoader(filepath)
        return loader.load()

    def split_documents(self,documents):
        return self.text_splitter.split_documents(documents)

    def process_documents(self,filepath):
        # Load documents
        documents = self.load_documents(filepath)
        #st.info("Loaded files")
        docs = self.split_documents(documents)
        #st.info("split documents")
        doc_name = create_name(filepath)
        vectorstore_name = os.path.join(Config.EMB_DIR,Config.VECTORSTORE_NAME,doc_name)
        if not os.path.exists(vectorstore_name):
            self.emb_model.generate_embeddings(docs,vectorstore_name)
        #st.info("Generated documents")




