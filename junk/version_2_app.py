from turtledemo.sorting_animate import instructions1

import streamlit as st
import ast
import os
from modules.chat_factory import ChatWithAssistant

asst=ChatWithAssistant()

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


# Initialize session states
if 'file_uploaded' not in st.session_state:
    st.session_state['file_uploaded'] = False
    st.session_state['next_step'] = 2

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'context' not in st.session_state:
    st.session_state['context'] = load_file(asst.context_path)
    # st.markdown(st.session_state['context'][:50])

if 'steps' not in st.session_state:
    st.session_state['steps'] = ast.literal_eval(load_file(asst.steps_path))
    # st.markdown(st.session_state['steps']['step_1'].keys())

if 'questions' not in st.session_state:
    st.session_state['questions'] = ast.literal_eval(load_file(asst.questions_path))
    st.session_state['file_uploaded'] = True
    # st.markdown(st.session_state['questions']['Question 1'].keys())
# Automatically load the context file from the specific path

# Chat Interface
if st.session_state['file_uploaded']:
    st.title("Report Generator")

    # Chat Container
    st.subheader("Report Generator Chat")
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for chat in st.session_state['chat_history']:
            role = "user" if chat['role'] == "user" else "assistant"
            avatar = "🧑" if role == "user" else "🤖"
            st.write(f"{avatar} **{role.capitalize()}:** {chat['content']}")
            #st.write(f"**{role}:** {chat['content']}")

        # Chat input in the container
        user_input = st.text_input("Type your message here:")

        if user_input:
            # Append user input to chat history
            st.session_state['chat_history'].append({"role": "user", "content": user_input})
            # role = "user"
            # st.write(f"🧑 **{role.capitalize()}:** {user_input}")
            st.session_state['thread'] = "thread_3KRoSmZpPln1gW8hhTW3gWmp" #asst.create_thread(user_input)

            for key,item in st.session_state['steps'].items():
                #st.markdown(str(item))
                instructions = item['instruction']
                user_input = "Stick to your instructions and continue. Do not give details about your working to the user. Just stick to the steps"
                role="user"
                st.write(f"🧑 **{role.capitalize()}:** {user_input}")
                if item['name']=="Report Objective":
                    instructions = instructions+f". Take a look at the context: {st.session_state['context']}"
                if item['name']=="Question":
                    instructions = f"Try to find the **Level** of this company for this question. {str(item['question'])}"
                bot_response = asst.run_assistant(st.session_state['thread'], user_input, instructions, role)
                role = "assistant"
                st.session_state['chat_history'].append({"role": "assistant", "content": bot_response})
                st.write(f"🤖 **{role.capitalize()}:** {bot_response}")

            # instructions = st.session_state['steps'][f"step_{str(st.session_state['next_step'])}"]["instruction"]
            #
            # bot_response = asst.run_assistant(st.session_state['thread'],user_input,instructions)
            #
            # st.session_state['chat_history'].append({"role": "assistant", "content": bot_response})
            #
            # if 'next_step' in bot_response.keys():
            #     st.session_state['next_step'] = st.session_state['next_step']+1
            #     # Loop through the steps and keep updating the report
            #     for item in st.session_state['steps']:
            #         instructions = item['instruction']
            #         user_input = "continue"
            #         bot_response = asst.run_assistant(st.session_state['thread'], user_input, instructions,"developer")
            #     st.rerun()
