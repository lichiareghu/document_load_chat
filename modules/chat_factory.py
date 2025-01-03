from config import Config
from openai import OpenAI
from modules.google_search import PDFSearcherDownloader
import logging
import os
from urllib.parse import urlparse
from modules.utils import get_filepath
from datetime import datetime

websearch = PDFSearcherDownloader()

class ChatWithAssistant:
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.assistant = Config.ASSISTANT_ID
        self.steps_path = get_filepath("steps.json","templates")
        self.context_path = get_filepath("context","templates")
        self.questions_path = get_filepath("questions.json","templates")
        self.vectorstore = "vs_YpmDyWR2c0zN1fwO1rqVRm4i"
        self.donotdelete = ['file-1sLJpyikYzretdxtDdpB62','file-4DtR2Yii8FqJBTf4vm1AvW','file-PJ9Bmz7w82bRVRjocWMaaQ']
        self.messages = []


    def create_thread(self,message,message_file=None):
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]
        if message_file:
            messages[0]["attachments"]= [
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ],
        return self.openai_client.beta.threads.create(messages = messages).id


    def get_assistant(self):
        my_assistant = self.openai_client.beta.assistants.retrieve(self.assistant)
        return my_assistant

    def get_thread(self,thread_id):
        thread = self.openai_client.beta.threads.retrieve(thread_id)
        return thread

    def create_files(self,filename):
        file = self.openai_client.files.create(
            file=open(filename, "rb"),
            purpose="assistants"
        )
        return file

    def create_vectorstore(self):
        vector_store = self.openai_client.beta.vector_stores.create(name="Documents")
        return vector_store

    def upload_files_to_vectorstore(self,vector_store,file_streams):
        file_batch = self.openai_client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store,
            files=file_streams
        )
        return file_batch
    def upload_file_to_vectorstore(self,vector_store,file_id):
        vector_store_file = self.openai_client.beta.vector_stores.files.create(
            vector_store_id=vector_store,
            file_id=file_id
        )

    def delete_files_from_vectorstore(self,vectorstore,files):
        deleted_vector_store_files=[]
        for file in files:
            deleted_vector_store_file = self.openai_client.beta.vector_stores.files.delete(
                vector_store_id=vectorstore,
                file_id=file
            )
            deleted_vector_store_files.append(deleted_vector_store_file)
        return deleted_vector_store_files

    def add_vector_store(self,vector_store):
        assistant = self.openai_client.beta.assistants.update(
            assistant_id=self.assistant,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        return assistant

    def modify_assistant(self, instructions):
        my_updated_assistant = self.openai_client.beta.assistants.update(
            self.assistant,
            instructions=instructions
        )
        return my_updated_assistant

    def delete_thread(self,thread_id):
        return self.openai_client.beta.threads.delete(thread_id)

    def file_cleanup(self,n):
        files = self.openai_client.files.list()
        # Collect all the assistants files
        ast_files = [file for file in files.data if file.purpose == 'assistants']
        sorted_files = sorted(ast_files, key=lambda x: x.created_at)
        # remove the donot delete
        files_to_delete = [file for file in sorted_files if file.id not in self.donotdelete]
        # Keep the most recent 10 files and delete the rest
        filtered = files_to_delete[:-n]
        deleted_files=[]
        if filtered:
            deleted_files = [self.openai_client.files.delete(file.id) for file in filtered]
        return deleted_files

    def update_vector_store(self,files):
        # Check if vector store is available
        if self.vectorstore:
            # Get the list of files from vectorstore
            vector_store_files = self.openai_client.beta.vector_stores.files.list(
                vector_store_id=self.vectorstore,
                limit=50
            )

            # Delete files if there are more than 10 files
            if len(vector_store_files.data)>50:
                # Prepare list of files to be deleted
                deletes = [item.id for item in vector_store_files.data if item.id not in self.donotdelete]
                self.delete_files_from_vectorstore(self.vectorstore,deletes[:-50])
                self.file_cleanup(50)

        # Create files and upload as vectorstore files
        file_list = [os.path.basename(urlparse(item).path) for item in files]
        file_paths = [os.path.join(Config.DOWNLOAD_DIR, name) for name in file_list]
        file_ids = [self.create_files(path).id for path in file_paths]
        success = []
        for id in file_ids:
            try:
                self.upload_file_to_vectorstore(self.vectorstore, id)
                success.append(id)
            except:
                pass
        return success

    def submit_tool_outputs(self, thread,run):
        # Define the list to store tool outputs
        tool_outputs = []
        print(run.required_action.submit_tool_outputs.tool_calls)

        # Loop through each tool in the required action section
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "web_search":
                # Create a vectorstore if not already available
                if not self.vectorstore:
                    self.vectorstore = self.create_vectorstore()
                    self.add_vector_store(self.vectorstore)
                # Search the internet and get the files
                output = websearch.search_and_download(tool.function.arguments)

                # Update the vectorstore
                self.update_vector_store(output)
            else:
                output = "Identified tool not found"

            # append the tool call outputs
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": str(output)
            })

        # Complete the run
        run = self.openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        print("Tool outputs submitted successfully.")


    def run_assistant(self,thread,message,instructions="",role="user"):
        # Create messages on the thread id
        self.openai_client.beta.threads.messages.create(
            thread_id=thread,
            role=role,
            content=message,
            metadata={"user_id":role}
        )

        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread,
            assistant_id=self.assistant,
            max_prompt_tokens=10000,
            additional_instructions=str(instructions),
            truncation_strategy={"type":"auto"}
        )
        if run.status == 'requires_action':
            print(run)
            self.submit_tool_outputs(thread,run)

        # Reload messages and check for the latest messages
        messages = list(
            self.openai_client.beta.threads.messages.list(thread_id=thread, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        return message_content.value




# class Completions:
#     def __init__(self):
#         """This function will load the assistant id and state variables
#         required for continuous contextual chat with the assistant"""
#         self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
#
#     def generate_response(self, context):
#         """This function will call the completions api
#         to generate response for the questions asked"""
#         response = self.openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=context
#         )
#
#         # Extract the content of response
#         cont = response.choices[0].message.content
#
#         # Return the content
#         return cont
#
#     def extract_content(self, input_string, pattern):
#         match = re.search(pattern, input_string, re.DOTALL)
#
#         if match:
#             return match.group(1)
#         else:
#             return None
# def websearch(question,company):
#     """Search the web"""
#     search = GoogleSearchAPIWrapper(google_api_key=Config.GOOGLE_API_KEY,
#                                         google_cse_id=Config.GOOGLE_CSE_ID)
#     response = search.run(f"Find the resorces required to find the answer to the question:{question} about the company:{company}")
#     return response
