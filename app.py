import os
import shutil

# import threading
import streamlit as st
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from config import Config

from modules.upload_factory import save_uploaded_file, delete_files
from modules.preprocess_factory import PreprocessPipeline
from modules.chat_factory import ChatWithAssistant
from modules.storage_factory import Data
from modules.utils import create_name


os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.EMB_DIR, exist_ok=True)

pipe=PreprocessPipeline(Config.MODEL_EMB)
user = Data("user")
asst = ChatWithAssistant()

# Simulate a long-running task
def create_thread_and_save(doc_name):
    thread_id = asst.create_thread()
    user.save_object(object={doc_name: thread_id})

def delete_chat(doc_name):
    upload_path = os.path.join(Config.UPLOAD_DIR,doc_name,".pdf")
    emb_path = os.path.join(Config.EMB_DIR,Config.VECTORSTORE_NAME,create_name(doc_name))

    # Find the objects for the user
    tmp = user.get_objects()
    # If the thread exist for the doc, delete it
    if tmp[doc_name]:
        try:
            asst.delete_thread(tmp[doc_name])
        except:
            pass
    # Delete the thread entry from the list of docs
    object = user.remove_object(doc_name)
    # Delete the document from the upload folder and the embeddings folder
    # if os.path.exists(upload_path):
    #     os.remove(upload_path)
    # if os.path.exists(emb_path):
    #     os.remove(emb_path)
    return f"Deleted chat for {doc_name}"

def load_chat(filename):
    file_path = os.path.join(Config.UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return f"Chat loaded for {filename}"
    return "File not found"

# Streamlit UI
st.title("PDF Chat Application")

# Sidebar with tabs
with st.sidebar:
    tab = st.radio("Select Tab", ["Load File", "Load Chat"])

if tab == "Load File":
    st.header("Upload and Process File")
    uploaded_files = st.file_uploader("Choose a file",
                                     type=["pdf"],  # You can restrict types (e.g., ["png", "jpg", "pdf"])
                                     accept_multiple_files=True,
                                     )

    file_names = []
    file_paths = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file)
            file_paths.append(file_path)
            st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("Process Files", key="process_files"):
            with st.spinner("Processing..."):
                for idx, file_path in enumerate(file_paths):
                    result = pipe.process_documents(file_path)
                    doc_name = create_name(file_path)
                    create_thread_and_save(doc_name=doc_name)
                    st.success(f"Processed: {os.path.basename(file_path)}")

elif tab == "Load Chat":
    st.header("Load Chat")
    if st.button("Refresh", key="refresh_docs"):
        st.rerun()

    def display_docs():
        chats = user.get_objects()
        if chats:
            for doc,chat in chats.items():
                col1, col2, col3 = st.columns([3, 1,1])
                col1.text(doc)
                unique_key = doc
                if col2.button("Load Chat", key=f"load_chat_{unique_key}"):
                    message = load_chat(doc)
                    st.info(message)
                if col3.button("Delete Chat", key=f"delete_chat_{unique_key}"):
                    message = delete_chat(doc)
                    st.warning(message)
        else:
            st.warning("No documents available in the docs folder.")

    display_docs()