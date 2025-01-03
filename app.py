import streamlit as st
import ast
import os
from modules.chat_factory import ChatWithAssistant
from modules.pdf_print2 import PDF
from modules.utils import build_json, save_results
from config import Config
import time
import json
import shutil
import io
from unidecode import unidecode

try:
    os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
except Exception as e:
    print(f"Failed to create directory {Config.DOWNLOAD_DIR}: {e}")

try:
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
except Exception as e:
    print(f"Failed to create directory {Config.UPLOAD_DIR}: {e}")

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

# Function to handle the step actions
def handle_step(step_name):
    with st.spinner(f"Processing {step_name}..."):
        tasks=steps[step_name]
        # Iterate through the steps defined in session state
        for task in tasks:
            item = st.session_state['steps'][task]
            instructions=""
            input=f"The company you are reporting on is {st.session_state['company']}"
            if "question" in list(item.keys()):
                input = input+'. '+str(item["question"])
            if 'tools' in list(item.keys()):
                tool = item["tools"]
            if 'instruction' in list(item.keys()):
                instructions=item['instruction']
            response = conversation_pipeline.run_assistant(
                st.session_state['thread'],
                input,
                instructions=instructions,
                role="user"
            )
            save_as ={task:{'content':str(response),'details':item}}
            st.session_state['steps_completed'].append(save_as)
            st.session_state['thread'] = conversation_pipeline.create_thread("Hi")
            time.sleep(5)
        st.session_state['show_output'] = True
        return response

def generate_report(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Set a default font before adding any content
    pdf.set_font('Arial', size=12)

    report_data = build_json(data,st.session_state['company'])
    for chapter, chapter_data in report_data.items():
        pdf.chapter_title(chapter, chapter_data['title'])
        if 'content' in chapter_data:
            pdf.content(chapter_data['content'])

        if 'subsections' in chapter_data:
            for subsection, subsection_data in chapter_data['subsections'].items():
                pdf.subchapter_title(subsection, subsection_data['title'])
                if 'content' in subsection_data:
                    pdf.content(subsection_data['content'])

                if 'questions' in subsection_data:
                    for subsubsection, question_data in subsection_data['questions'].items():
                        pdf.question(subsubsection, question_data['question'])
                        pdf.content(question_data['content'])
    # Save PDF
    filename = f"ESG_{st.session_state['company']}_Report"
    pdf.output("dynamic_report.pdf")
    # Save PDF to a BytesIO object
    pdf_file = io.BytesIO()
    pdf.output(pdf_file)
    pdf_file.seek(0)
    return pdf_file
# Initialize the conversational pipeline
@st.cache_resource
def load_pipeline():
    return ChatWithAssistant()


conversation_pipeline = load_pipeline()
steps = {'do_research':['step_0'],
         'collect_data':['step_2','step_3'],#,'step_4','step_5','step_6','step_7','step_8','step_9','step_10'], #'step_11','step_12','step_13','step_14','step_15','step_16','step_17','step_18','step_19','step_20'],
         'generate_report':['step_5']}

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
# Page layout
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'input_page'
# Initialise show output
if 'show_output' not in st.session_state:
    st.session_state['show_output']=False
if 'steps_completed' not in st.session_state:
    st.session_state['steps_completed']=[]
# Input page
if st.session_state['current_page'] == 'input_page':
    st.title("ESG Report Tool")

    # Input text box for company name or web address
    company_input = st.text_input("Enter Company Name or Web Address:")
    st.session_state['company'] = company_input

    # Start button
    if st.button("Start"):
        if company_input:
            st.session_state['current_page'] = 'action_page'
            st.rerun()
        else:
            st.warning("Please enter a company name or web address.")

# Action page
if st.session_state['current_page'] == 'action_page':

    # Back button at the top right
    top_right_col = st.columns([9, 1])
    with top_right_col[1]:
        # Back button to restart
        if st.button("Back"):
            if st.session_state['show_output'] == True:
                st.session_state['current_page'] = 'action_page'
            else:
                st.session_state['current_page'] = 'input_page'
            st.session_state['steps_completed'] = []
            st.session_state['show_output'] = False
            st.rerun()

    st.title(f"Working on company {st.session_state['company']}")

    # Sidebar for actions
    with st.sidebar:
        st.subheader("Actions")
        if st.button("Do Research"):
            handle_step("do_research")
            # Delete all files and subdirectories
            try:
                shutil.rmtree(Config.DOWNLOAD_DIR)
                os.makedirs(Config.DOWNLOAD_DIR)
                print(f"Cleared: {Config.DOWNLOAD_DIR}")
            except Exception as e:
                print(f"Failed to clear directory {Config.DOWNLOAD_DIR}: {e}")

        if st.button("Collect Data"):
            handle_step("collect_data")

        if st.button("Generate Report"):
            st.session_state['generate_report'] = False
            pdf_file = generate_report(st.session_state['steps_completed'])
            if pdf_file:
                st.session_state['generate_report'] = True
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name="dynamic_report.pdf",
                    mime="application/pdf",
                )
            else:
                st.error("Report generation failed.")

    # # Display container for the latest output
    # if st.session_state['show_output']:
    #     st.subheader("Process Output")
    #     last_step = st.session_state['steps_completed'][-1]
    #     st.info(f"{'last_step'}: {last_step}")

    # Display completed steps
    if st.session_state['steps_completed']:
        st.subheader("Steps Completed")
        for step in st.session_state['steps_completed']:
            st.write(step)

        json_string = json.dumps(st.session_state['steps_completed'], indent=4)

        # Add a download button
        st.download_button(
            label="Download Results",
            data=json_string,
            file_name="completed_steps.json",
            mime="application/json",
        )



