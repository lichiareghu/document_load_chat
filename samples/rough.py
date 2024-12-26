import openai
import streamlit as st
from modules.chat_factory import ChatWithAssistant
import time
import os
from config import Config
from modules.preprocess_factory import PreprocessPipeline
from modules.upload_factory import save_uploaded_file, list_files
import logging
from modules.retreival_factory import KnowledgeRetriver, OpenAIRetriver
from modules.vectorstore_factory import FaissVectorStore
from modules.storage_factory import Data
from modules.utils import create_name

# Set up your OpenAI API key
buddy = ChatWithAssistant()
# Initialise the knowledge retreiver
ret = KnowledgeRetriver()
user = Data("user")

# Create a directory to store uploaded files
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.EMB_DIR, exist_ok=True)

# Streamlit UI setup
st.title("PDF chat Playground")



# Create a session state variable for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    thread = user.get_objects()
    if thread:
        st.session_state.thread_id = thread[0]["thread_id"]
    else:
        st.session_state.thread_id = buddy.create_thread()
        user.save_object(object = {"thread_id":st.session_state.thread_id})
else:
    buddy.thread = st.session_state.thread_id


# with st.sidebar:
#     tab1, tab2 = st.tabs(["view", "modify"])
#     with tab1:
#         st.header("View Instructions")
#         if st.button("Get Assistant", type="primary"):
#             assistant = buddy.get_assistant()
#             st.write(assistant.instructions)
#     with tab2:
#         st.header("Modify Instructions")
#         inst = st.text_input("Modified instruction", "Type the instruction here")
#         if st.button("Modify Assistant", type="primary"):
#             success = buddy.modify_assistant(inst)
#             st.write(success.instructions)

with st.sidebar:
    tab1, tab2, tab3 = st.tabs(["Files", "Tests", "Conversations"])
    with tab1:
        st.header("File Uploader")
        if st.button("Upload Files", type="primary"):
            uploaded_files = st.file_uploader(
                "Upload PDF",
                type=["pdf"],  # You can restrict types (e.g., ["png", "jpg", "pdf"])
                accept_multiple_files=True,  # Allow multiple files to be uploaded
            )

            # Display uploaded files
            if uploaded_files:
                file_names = []
                file_paths = []
                pipe = PreprocessPipeline(Config.MODEL_EMB)
                with st.spinner(text="Uploading files..."):
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(Config.UPLOAD_DIR, uploaded_file.name)
                        load_files(uploaded_file)
                        file_paths.append(file_path)
                        file_names.append(uploaded_file.name)
                    st.session_state.file_paths = file_paths
                    st.session_state.file_names = file_names
                    st.success(f"Successfully saved files {file_names}")



        # if st.button(" Process Files", type="primary"):
        #     with st.spinner(text="Processing saved files..."):
        #         pipe = PreprocessPipeline(Config.MODEL_EMB)
        #         for path in file_paths:
        #             pipe.process_documents(path)
        #             if user.get_objects():
        #                 thread_id = buddy.create_thread()
        #                 doc_name = create_name(path)
        #                 user.save_object(object={doc_name: thread_id})
        #         st.success(f"Successfully processed saved files {file_names}")
    with tab2:
        if "file_paths" in list(st.session_state):
            for file_path in st.session_state["file_paths"]:
                if st.button("Process File", type="primary"):
                    with st.spinner(text=f"Processing file..."):
                        pipe.process_documents(file_path)
                        if user.get_objects():
                            thread_id = buddy.create_thread()
                            doc_name = create_name(file_path)
                            user.save_object(object={doc_name: thread_id})
                        st.success(f"Successfully saved files {file_path}")
        else:
            st.write("No uploded files to process")

        # st.header("Tests")
        # inp = st.text_input("Type the question here")
        # if st.button("Run Test", type="primary") and inp:
        #     reto = OpenAIRetriver()
        #     context = ret.retreive_context(st.session_state.vectorstore.vectorstore_faiss,
        #                                    inp)
        #     response = reto.retreive_context(f"Find the answer to question {inp} from context {context}")
        #     st.markdown(str(response["result"]))

    with tab3:
        # st.header("Chat with your PDF")
        # Load the vectorstore

        for item in list_files():
            if st.button(f"{os.path.basename(item)}"):
                with st.spinner(text="Loading files..."):
                    # Load History
                    history = user.get_objects()
                    # Build the embedding path
                    doc_name = create_name(item)
                    try:
                        emb_path = os.path.join(Config.EMB_DIR,Config.VECTORSTORE_NAME,doc_name)
                        st.session_state.vectorstore = FaissVectorStore(Config.MODEL_EMB, emb_path)
                        st.session_state.thread_id = history[doc_name]
                        st.write(f"Chatting with: {item}")
                    except:
                        st.write("Please process and load your files first")
                    st.success("Done!")
        # chat = st.select_slider(
        #     "Select a PDF to chat with",
        #     options=list_files(),
        # )
        # st.write("Chatting with", chat[:10])

#
# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Type your questions here"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f"You: {prompt}")
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Get context
    context = ret.retreive_context(st.session_state.vectorstore.vectorstore_faiss,prompt )
    tmp = f"Use this context {str(context['result'])} to answer this question from the user {prompt}."
    #response = f"Jack: {context.result}"
    #st.write(str(context.result))
    response = f"Jack: {buddy.run_assistant(tmp)}"

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response})