import streamlit as st
import ast
import os
from modules.chat_factory import ChatWithAssistant
from modules.report_factory import ReportAssistant
import time
#report = ReportAssistant()

def load_file(path):
    try:
        data = None
        with open(path, "r", encoding="utf-8") as file:
            data = file.read()
            return data
    except FileNotFoundError:
        return data
    except PermissionError:
        return data


# Initialize the conversational pipeline
@st.cache_resource
def load_pipeline():
    return ChatWithAssistant()


conversation_pipeline = load_pipeline()

# Initialize session state for the chat
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
if "thread" not in st.session_state:
    st.session_state['thread'] = conversation_pipeline.create_thread("Hi")

if 'context' not in st.session_state:
    st.session_state['context'] = load_file(conversation_pipeline.context_path)

if 'steps' not in st.session_state:
    st.session_state['steps'] = ast.literal_eval(load_file(conversation_pipeline.steps_path))

if 'questions' not in st.session_state:
    st.session_state['questions'] = ast.literal_eval(load_file(conversation_pipeline.questions_path))
    st.session_state['file_uploaded'] = True

# Title of the app
st.title("AI Chat Assistant")

# Input box for user to provide the initial chat message
with st.form(key="user_input_form"):
    user_input = st.text_input("Enter your message to start the conversation:", "")
    submit_button = st.form_submit_button("Send")


# Function to update chat history
def update_chat_history(user, assistant):
    st.session_state.chat_history.append((user, assistant))

# Handle the input and update conversation
if submit_button and user_input:
    placeholder = st.empty()  # Placeholder to dynamically update messages

    # Iterate through the steps defined in session state
    for key, item in st.session_state['steps'].items():
        # Fetch instructions for the current step
        instructions = item["instruction"]
        addl_inst = ""
        if item['name'] == "Report Objective":
            instructions = instructions + f". Take a look at the context: {st.session_state['context']}"
        if item['name'] == "Question":
            instructions = f"Try to find the **Level** of this company for this question. {str(item['question'])}"

        # Send the user's message and instructions to the assistant
        with placeholder.container():
            with st.spinner(f"Processing step: {item['name']}..."):
                response = conversation_pipeline.run_assistant(
                    st.session_state['thread'],
                    user_input,
                    instructions,
                    "user"
                )

        # Update chat history
        update_chat_history(user_input, response)

        # Display the updated chat history dynamically
        placeholder.empty()  # Clear the spinner
        #for user_message, assistant_message in st.session_state.chat_history:
        st.chat_message("User").markdown(user_input)
        st.chat_message("Assistant").markdown(response)

        # Update user input with assistant's response for the next step
        user_input = "Continue"  # Simulate conversational flow for subsequent steps
