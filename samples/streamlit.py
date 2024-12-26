import os
import time
import threading
import streamlit as st
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
DOCS_FOLDER = 'docs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCS_FOLDER, exist_ok=True)

# Simulate a long-running task
def process_long_task():
    time.sleep(5)  # Simulate processing delay
    return "File processed successfully"

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(uploaded_file.name))
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_docs():
    return os.listdir(DOCS_FOLDER)

def load_chat(filename):
    file_path = os.path.join(DOCS_FOLDER, filename)
    if os.path.exists(file_path):
        return f"Chat loaded for {filename}"
    return "File not found"

# Streamlit UI
st.title("Chat Sidebar Application")

# Sidebar with tabs
with st.sidebar:
    tab = st.radio("Select Tab", ["Load File", "Load Chat"])

if tab == "Load File":
    st.header("Upload and Process File")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file)
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("Process File"):
            with st.spinner("Processing..."):
                result = process_long_task()
                st.success(result)

elif tab == "Load Chat":
    st.header("Load Chat")
    docs = list_docs()

    if docs:
        for doc in docs:
            col1, col2 = st.columns([3, 1])
            col1.text(doc)
            if col2.button("Load Chat", key=doc):
                message = load_chat(doc)
                st.info(message)
    else:
        st.warning("No documents available in the docs folder.")
